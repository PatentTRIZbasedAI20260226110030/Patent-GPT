import logging
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.config import Settings
from app.models.state import AgentState
from app.prompts.evasion import EVASION_HUMAN, EVASION_SYSTEM
from app.prompts.triz_expert import TRIZ_EXPERT_SYSTEM, TRIZ_IDEA_GENERATION_HUMAN
from app.services.patent_searcher import PatentSearcher

logger = logging.getLogger(__name__)


def should_evade(state: dict[str, Any], threshold: float, max_attempts: int) -> bool:
    return state["max_similarity_score"] > threshold and state["evasion_count"] < max_attempts


class ReasoningAgent:
    def __init__(self, settings: Settings, patent_searcher: PatentSearcher):
        self.settings = settings
        self.patent_searcher = patent_searcher
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )
        self.idea_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", TRIZ_EXPERT_SYSTEM),
                ("human", TRIZ_IDEA_GENERATION_HUMAN),
            ]
        )
        self.evasion_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EVASION_SYSTEM),
                ("human", EVASION_HUMAN),
            ]
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("generate_idea", self._generate_idea_node)
        graph.add_node("search_prior_art", self._search_prior_art_node)
        graph.add_node("evaluate", self._evaluate_node)
        graph.add_node("evade", self._evade_node)
        graph.add_node("finalize", self._finalize_node)

        graph.set_entry_point("generate_idea")
        graph.add_edge("generate_idea", "search_prior_art")
        graph.add_edge("search_prior_art", "evaluate")
        graph.add_conditional_edges(
            "evaluate",
            self._route_after_evaluate,
            {"evade": "evade", "finalize": "finalize"},
        )
        graph.add_edge("evade", "search_prior_art")
        graph.add_edge("finalize", END)

        return graph.compile()

    def _route_after_evaluate(self, state: AgentState) -> str:
        if should_evade(
            state,
            threshold=self.settings.SIMILARITY_THRESHOLD,
            max_attempts=self.settings.MAX_EVASION_ATTEMPTS,
        ):
            return "evade"
        return "finalize"

    async def _generate_idea_node(self, state: AgentState) -> dict:
        triz_text = ", ".join(
            f"#{p.number} {p.name_ko}({p.name_en})" for p in state["triz_principles"]
        )
        chain = self.idea_prompt | self.llm
        response = await chain.ainvoke(
            {
                "problem_description": state["user_problem"],
                "triz_principles": triz_text,
            }
        )
        return {
            "current_idea": response.content,
            "reasoning_trace": state["reasoning_trace"]
            + [f"[아이디어 생성] TRIZ 원리 {triz_text} 적용"],
        }

    async def _search_prior_art_node(self, state: AgentState) -> dict:
        query = f"{state['user_problem']} {state['current_idea'][:200]}"
        results = await self.patent_searcher.search(query)
        max_score = max((p.similarity_score for p in results), default=0.0)
        return {
            "similar_patents": results,
            "max_similarity_score": max_score,
            "reasoning_trace": state["reasoning_trace"]
            + [f"[선행기술 조사] {len(results)}건 검색, 최대 유사도: {max_score:.1%}"],
        }

    async def _evaluate_node(self, state: AgentState) -> dict:
        threshold = self.settings.SIMILARITY_THRESHOLD
        score = state["max_similarity_score"]
        if score > threshold:
            msg = f"[평가] 유사도 {score:.1%} > {threshold:.0%} → 회피 설계 필요"
        else:
            msg = f"[평가] 유사도 {score:.1%} ≤ {threshold:.0%} → 독창성 확보"
        return {
            "reasoning_trace": state["reasoning_trace"] + [msg],
        }

    async def _evade_node(self, state: AgentState) -> dict:
        patents_text = "\n".join(
            f"- {p.title} (유사도: {p.similarity_score:.1%}): {p.abstract[:100]}..."
            for p in state["similar_patents"][:3]
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
            "reasoning_trace": state["reasoning_trace"]
            + [f"[회피 설계 #{new_count}] 새로운 아이디어 생성"],
        }

    async def _finalize_node(self, state: AgentState) -> dict:
        return {
            "final_idea": state["current_idea"],
            "reasoning_trace": state["reasoning_trace"] + ["[완료] 최종 아이디어 확정"],
        }

    async def run(self, initial_state: AgentState) -> AgentState:
        result = await self.graph.ainvoke(initial_state)
        return result
