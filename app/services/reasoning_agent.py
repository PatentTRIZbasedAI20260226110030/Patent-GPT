import json
import logging
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph

from app.config import Settings, get_llm
from app.models.patent_draft import SimilarPatent
from app.models.state import AgentState
from app.models.triz import TRIZPrinciple
from app.prompts.crag import CRAG_EVALUATION_HUMAN, CRAG_EVALUATION_SYSTEM
from app.prompts.evasion import EVASION_HUMAN, EVASION_SYSTEM
from app.prompts.novelty import NOVELTY_EVALUATION_HUMAN, NOVELTY_EVALUATION_SYSTEM
from app.prompts.triz_expert import TRIZ_EXPERT_SYSTEM, TRIZ_IDEA_GENERATION_HUMAN
from app.services.patent_searcher import PatentSearcher
from app.services.triz_classifier import classify_triz
from app.utils.kipris_client import KIPRISClient

logger = logging.getLogger(__name__)


def format_triz_text(principles: list[TRIZPrinciple]) -> str:
    """Format TRIZ principles for prompt injection."""
    return ", ".join(f"#{p.number} {p.name_ko}({p.name_en})" for p in principles)


def format_patents_summary(
    patents: list[SimilarPatent], max_count: int = 5, abstract_len: int = 150
) -> str:
    """Format similar patents for prompt injection."""
    if not patents:
        return "(선행기술 없음)"
    return "\n".join(
        f"- {p.title} (유사도: {p.similarity_score:.1%}): {p.abstract[:abstract_len]}"
        for p in patents[:max_count]
    )


def route_after_evaluate_novelty(state: dict[str, Any], threshold: float) -> str:
    """Route after novelty evaluation: novel → draft, not novel → evade or draft."""
    if state["novelty_score"] >= threshold:
        return "draft_patent"
    if state["evasion_count"] >= state["max_evasion_attempts"]:
        return "draft_patent"
    return "evade"


def route_after_evaluate_context(state: dict[str, Any]) -> str:
    """Route after CRAG context evaluation: sufficient → generate, insufficient → kipris."""
    if state["context_sufficient"]:
        return "generate_idea"
    return "search_kipris"


class PatentPipeline:
    """Full patent generation pipeline as a LangGraph StateGraph."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = get_llm(settings, temperature=0.7)
        self.patent_searcher = PatentSearcher(settings)
        self.kipris_client = KIPRISClient(settings)

        # Prompts
        self.idea_prompt = ChatPromptTemplate.from_messages(
            [("system", TRIZ_EXPERT_SYSTEM), ("human", TRIZ_IDEA_GENERATION_HUMAN)]
        )
        self.evasion_prompt = ChatPromptTemplate.from_messages(
            [("system", EVASION_SYSTEM), ("human", EVASION_HUMAN)]
        )
        self.novelty_prompt = ChatPromptTemplate.from_messages(
            [("system", NOVELTY_EVALUATION_SYSTEM), ("human", NOVELTY_EVALUATION_HUMAN)]
        )
        self.crag_prompt = ChatPromptTemplate.from_messages(
            [("system", CRAG_EVALUATION_SYSTEM), ("human", CRAG_EVALUATION_HUMAN)]
        )

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("classify_triz", self._classify_triz_node)
        graph.add_node("search_internal", self._search_internal_node)
        graph.add_node("evaluate_context", self._evaluate_context_node)
        graph.add_node("search_kipris", self._search_kipris_node)
        graph.add_node("generate_idea", self._generate_idea_node)
        graph.add_node("evaluate_novelty", self._evaluate_novelty_node)
        graph.add_node("evade", self._evade_node)
        graph.add_node("draft_patent", self._draft_patent_node)

        graph.set_entry_point("classify_triz")
        graph.add_edge("classify_triz", "search_internal")
        graph.add_edge("search_internal", "evaluate_context")
        graph.add_conditional_edges(
            "evaluate_context",
            route_after_evaluate_context,
            {"generate_idea": "generate_idea", "search_kipris": "search_kipris"},
        )
        graph.add_edge("search_kipris", "generate_idea")
        graph.add_edge("generate_idea", "evaluate_novelty")
        graph.add_conditional_edges(
            "evaluate_novelty",
            lambda state: route_after_evaluate_novelty(
                state,
                threshold=self.settings.SIMILARITY_THRESHOLD,
            ),
            {"draft_patent": "draft_patent", "evade": "evade"},
        )
        graph.add_edge("evade", "search_internal")
        graph.add_edge("draft_patent", END)

        return graph.compile()

    # ── Node implementations ──────────────────────────────────────

    async def _classify_triz_node(self, state: AgentState) -> dict:
        principles = await classify_triz(
            state["user_problem"],
            state["technical_field"],
            self.settings,
            keyword=state.get("keyword"),
        )
        return {
            "triz_principles": principles,
            "current_step": "classify_triz",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[TRIZ 분류] {len(principles)}개 원리 선정"],
        }

    async def _search_internal_node(self, state: AgentState) -> dict:
        query = state["user_problem"]
        keyword = state.get("keyword", "")
        if keyword:
            query = f"{keyword} {query}".strip()
        if state["current_idea"]:
            query = f"{query} {state['current_idea'][:200]}"
        results = await self.patent_searcher.search(query)
        max_score = max((p.similarity_score for p in results), default=0.0)
        return {
            "similar_patents": results,
            "max_similarity_score": max_score,
            "current_step": "search_internal",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[내부 검색] {len(results)}건 검색, 최대 유사도: {max_score:.1%}"],
        }

    async def _evaluate_context_node(self, state: AgentState) -> dict:
        results = state["similar_patents"]
        # Quick check: if fewer than 3 results, context is insufficient
        if len(results) < 3:
            return {
                "context_sufficient": False,
                "current_step": "evaluate_context",
                "reasoning_trace": state["reasoning_trace"]
                + [f"[CRAG 평가] 검색 결과 {len(results)}건 < 3건 → 외부 검색 필요"],
            }

        patents_summary = "\n".join(
            f"- {p.title}: {p.abstract[:100]}..." for p in results[:5]
        )
        chain = self.crag_prompt | self.llm
        response = await chain.ainvoke(
            {
                "user_problem": state["user_problem"],
                "technical_field": state["technical_field"],
                "num_results": len(results),
                "patents_summary": patents_summary,
            }
        )
        try:
            data = json.loads(response.content)
            sufficient = data.get("sufficient", True)
        except (json.JSONDecodeError, AttributeError):
            sufficient = True  # default to sufficient if parsing fails

        return {
            "context_sufficient": sufficient,
            "current_step": "evaluate_context",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[CRAG 평가] 컨텍스트 {'충분' if sufficient else '불충분'}"],
        }

    async def _search_kipris_node(self, state: AgentState) -> dict:
        keyword = state.get("keyword") or state["user_problem"][:50]
        patents = await self.kipris_client.search_patents(keyword, num_of_rows=20)
        kipris_as_patents = [
            SimilarPatent(
                title=p.get("title", ""),
                abstract=p.get("abstract", ""),
                application_number=p.get("application_number", ""),
                similarity_score=0.0,
            )
            for p in patents
        ]
        merged = state["similar_patents"] + kipris_as_patents
        max_score = max((p.similarity_score for p in merged), default=0.0)
        return {
            "similar_patents": merged,
            "max_similarity_score": max_score,
            "current_step": "search_kipris",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[KIPRIS 검색] 외부 API에서 {len(patents)}건 추가 수집"],
        }

    async def _generate_idea_node(self, state: AgentState) -> dict:
        triz_text = format_triz_text(state["triz_principles"])
        chain = self.idea_prompt | self.llm
        response = await chain.ainvoke(
            {
                "problem_description": state["user_problem"],
                "triz_principles": triz_text,
            }
        )
        return {
            "current_idea": response.content,
            "current_step": "generate_idea",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[아이디어 생성] TRIZ 원리 {triz_text} 적용"],
        }

    async def _evaluate_novelty_node(self, state: AgentState) -> dict:
        patents_text = format_patents_summary(
            state["similar_patents"], max_count=5, abstract_len=150
        )

        chain = self.novelty_prompt | self.llm
        response = await chain.ainvoke(
            {
                "current_idea": state["current_idea"],
                "similar_patents_text": patents_text,
            }
        )
        try:
            data = json.loads(response.content)
            novelty_score = float(data.get("novelty_score", 0.5))
            reasoning = data.get("reasoning", "")
        except (json.JSONDecodeError, AttributeError, ValueError):
            novelty_score = 0.5
            reasoning = "평가 파싱 실패, 기본값 사용"

        is_novel = novelty_score >= self.settings.SIMILARITY_THRESHOLD
        status = "독창적" if is_novel else "유사"
        return {
            "novelty_score": novelty_score,
            "novelty_reasoning": reasoning,
            "current_step": "evaluate_novelty",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[신규성 평가] 점수: {novelty_score:.1%} → {status}"],
        }

    async def _evade_node(self, state: AgentState) -> dict:
        patents_text = format_patents_summary(
            state["similar_patents"], max_count=3, abstract_len=100
        )
        chain = self.evasion_prompt | self.llm
        response = await chain.ainvoke(
            {
                "problem_description": state["user_problem"],
                "current_idea": state["current_idea"],
                "similar_patents_text": patents_text,
                "max_similarity_score": state["max_similarity_score"],
            }
        )
        new_count = state["evasion_count"] + 1
        return {
            "current_idea": response.content,
            "evasion_count": new_count,
            "current_step": "evade",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[회피 설계 #{new_count}] 새로운 아이디어 생성"],
        }

    async def _draft_patent_node(self, state: AgentState) -> dict:
        from app.services.draft_generator import generate_draft

        triz_text = format_triz_text(state["triz_principles"])
        draft, docx_path = await generate_draft(
            idea=state["current_idea"],
            problem_description=state["user_problem"],
            triz_principles_text=triz_text,
            settings=self.settings,
        )
        return {
            "final_idea": state["current_idea"],
            "patent_draft": draft,
            "docx_path": docx_path,
            "current_step": "draft_patent",
            "reasoning_trace": state["reasoning_trace"] + ["[완료] 특허 명세서 초안 생성"],
        }

    # ── Public API ────────────────────────────────────────────────

    async def run(self, initial_state: AgentState) -> AgentState:
        result = await self.graph.ainvoke(initial_state)
        return result

    async def stream(self, initial_state: AgentState):
        """Yield state updates after each node for SSE streaming."""
        async for event in self.graph.astream(initial_state):
            yield event
