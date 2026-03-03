# Backend Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor Patent-GPT backend to an all-in-LangGraph pipeline with Gemini 2.0 Flash, CRAG retrieval, and novelty evaluation — working prototype for March 4th demo.

**Architecture:** Single LangGraph StateGraph with 8 nodes (classify_triz → search_internal → evaluate_context → [search_kipris fallback] → generate_idea → evaluate_novelty → [evade loop] → draft_patent). All LLM calls use Gemini 2.0 Flash via langchain-google-genai. Embeddings stay OpenAI text-embedding-3-small.

**Tech Stack:** FastAPI, LangGraph, langchain-google-genai (Gemini 2.0 Flash), ChromaDB, CrossEncoder, sse-starlette, pytest

---

### Task 1: Update dependencies and config

**Files:**
- Modify: `pyproject.toml`
- Modify: `app/config.py`
- Modify: `.env.example`
- Test: `tests/test_config.py`

**Step 1: Update pyproject.toml**

Add `langchain-google-genai` and `sse-starlette` to dependencies:

```toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "langchain>=0.3.0",
    "langchain-google-genai>=2.0.0",
    "langchain-openai>=0.2.0",
    "langchain-community>=0.3.0",
    "langgraph>=0.2.0",
    "chromadb>=0.5.0",
    "rank-bm25>=0.2.2",
    "sentence-transformers>=3.0.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "python-docx>=1.1.0",
    "httpx>=0.27.0",
    "sse-starlette>=1.6.0",
]
```

**Step 2: Update app/config.py**

Replace `LLM_MODEL` and `LLM_MODEL_MINI` with `GEMINI_MODEL` and add `GOOGLE_API_KEY`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str = ""  # now optional, only for embeddings
    GOOGLE_API_KEY: str       # required, for Gemini
    KIPRIS_API_KEY: str = ""

    # Model settings
    GEMINI_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Search settings
    SIMILARITY_THRESHOLD: float = 0.8
    MAX_EVASION_ATTEMPTS: int = 3
    RETRIEVAL_TOP_K: int = 20
    RERANK_TOP_K: int = 5

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chromadb"

    model_config = {"env_file": ".env", "extra": "ignore"}


def get_settings() -> Settings:
    return Settings()
```

**Step 3: Update .env.example**

```env
GOOGLE_API_KEY=                          # Google AI Studio API key (required)
OPENAI_API_KEY=                          # OpenAI API key (for embeddings)
KIPRIS_API_KEY=                          # KIPRISplus API key
GEMINI_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.8
MAX_EVASION_ATTEMPTS=3
RETRIEVAL_TOP_K=20
RERANK_TOP_K=5
CHROMA_PERSIST_DIR=./data/chromadb
```

**Step 4: Update test**

Rewrite `tests/test_config.py`:

```python
def test_settings_loads_defaults():
    """Settings should have sensible defaults even without .env file."""
    from app.config import Settings

    settings = Settings(
        GOOGLE_API_KEY="test-google-key",
    )
    assert settings.GEMINI_MODEL == "gemini-2.0-flash"
    assert settings.EMBEDDING_MODEL == "text-embedding-3-small"
    assert settings.SIMILARITY_THRESHOLD == 0.8
    assert settings.MAX_EVASION_ATTEMPTS == 3
    assert settings.RETRIEVAL_TOP_K == 20
    assert settings.RERANK_TOP_K == 5


def test_settings_requires_google_api_key(monkeypatch):
    """Settings should fail without required GOOGLE_API_KEY."""
    import pytest
    from pydantic import ValidationError

    from app.config import Settings

    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings()
```

**Step 5: Run test**

Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 6: Install new deps**

Run: `pip install -e ".[dev]"`

**Step 7: Commit**

```bash
git add pyproject.toml app/config.py .env.example tests/test_config.py
git commit -m "feat: swap config to Gemini 2.0 Flash + add GOOGLE_API_KEY"
```

---

### Task 2: Update AgentState with new fields

**Files:**
- Modify: `app/models/state.py`
- Modify: `tests/test_models.py`

**Step 1: Rewrite state.py**

```python
from typing import TypedDict

from app.models.patent_draft import SimilarPatent
from app.models.triz import TRIZPrinciple


class AgentState(TypedDict):
    user_problem: str
    technical_field: str
    triz_principles: list[TRIZPrinciple]
    current_idea: str
    similar_patents: list[SimilarPatent]
    max_similarity_score: float
    novelty_score: float
    novelty_reasoning: str
    context_sufficient: bool
    evasion_count: int
    final_idea: str
    reasoning_trace: list[str]
    current_step: str
```

**Step 2: Update test_models.py — fix test_agent_state_keys**

Replace the `test_agent_state_keys` function:

```python
def test_agent_state_keys():
    from app.models.state import AgentState

    state: AgentState = {
        "user_problem": "test",
        "technical_field": "",
        "triz_principles": [],
        "current_idea": "",
        "similar_patents": [],
        "max_similarity_score": 0.0,
        "novelty_score": 0.0,
        "novelty_reasoning": "",
        "context_sufficient": False,
        "evasion_count": 0,
        "final_idea": "",
        "reasoning_trace": [],
        "current_step": "",
    }
    assert state["context_sufficient"] is False
    assert state["evasion_count"] == 0
    assert state["novelty_score"] == 0.0
```

**Step 3: Run tests**

Run: `pytest tests/test_models.py tests/test_models_triz.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add app/models/state.py tests/test_models.py
git commit -m "feat: extend AgentState with novelty, CRAG, and step tracking fields"
```

---

### Task 3: Add new prompts (novelty + CRAG)

**Files:**
- Create: `app/prompts/novelty.py`
- Create: `app/prompts/crag.py`
- Modify: `app/prompts/classifier.py` — no changes needed, reuse as-is

**Step 1: Create app/prompts/novelty.py**

```python
NOVELTY_EVALUATION_SYSTEM = """당신은 특허 심사관 수준의 특허성 평가 전문가입니다.
발명 아이디어와 유사 선행 기술을 비교하여 신규성과 진보성을 평가합니다.

평가 기준:
1. 신규성(Novelty): 선행 기술에 동일한 구성이 존재하는가?
2. 진보성(Inventive Step): 선행 기술로부터 용이하게 도출 가능한가?

반드시 아래 JSON 형식으로 응답하세요:
{{"novelty_score": 0.0~1.0, "reasoning": "평가 근거", "is_novel": true/false}}

- novelty_score: 1.0 = 완전 독창적, 0.0 = 선행 기술과 동일
- is_novel: novelty_score >= 0.5이면 true
- reasoning: 한국어로 구체적인 평가 근거"""

NOVELTY_EVALUATION_HUMAN = """발명 아이디어:
{current_idea}

유사 선행 특허:
{similar_patents_text}

위 발명 아이디어의 신규성과 진보성을 평가하세요."""
```

**Step 2: Create app/prompts/crag.py**

```python
CRAG_EVALUATION_SYSTEM = """당신은 특허 선행기술 조사 전문가입니다.
검색된 선행기술 문서들이 발명 아이디어의 신규성 평가에 충분한지 판단합니다.

반드시 아래 JSON 형식으로 응답하세요:
{{"sufficient": true/false, "reasoning": "판단 근거"}}

판단 기준:
- 검색된 문서가 발명의 기술 분야와 관련이 있는가?
- 유사한 기술적 접근이나 구조가 포함되어 있는가?
- 문서 수가 유의미한 비교를 하기에 충분한가? (최소 3건)"""

CRAG_EVALUATION_HUMAN = """기술적 문제: {user_problem}
기술 분야: {technical_field}

검색된 선행기술 ({num_results}건):
{patents_summary}

위 검색 결과가 특허 신규성 평가에 충분한 선행기술을 포함하고 있는지 판단하세요."""
```

**Step 3: Commit**

```bash
git add app/prompts/novelty.py app/prompts/crag.py
git commit -m "feat: add novelty evaluation and CRAG context prompts"
```

---

### Task 4: Refactor TRIZClassifier into a node function

**Files:**
- Modify: `app/services/triz_classifier.py`
- Test: `tests/test_triz_classifier.py` — no changes needed (tests `parse_principles_response`, still valid)

**Step 1: Rewrite triz_classifier.py**

Swap `ChatOpenAI` to `ChatGoogleGenerativeAI`, keep `parse_principles_response` as a standalone function:

```python
import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import Settings
from app.models.triz import TRIZPrinciple, load_triz_principles
from app.prompts.classifier import TRIZ_CLASSIFIER_HUMAN, TRIZ_CLASSIFIER_SYSTEM

logger = logging.getLogger(__name__)


def parse_principles_response(content: str) -> list[TRIZPrinciple]:
    try:
        data = json.loads(content)
        return [TRIZPrinciple(**item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse TRIZ classifier response: {e}")
        return []


async def classify_triz(
    problem_description: str,
    technical_field: str,
    settings: Settings,
) -> list[TRIZPrinciple]:
    """Classify problem into top-3 TRIZ principles using Gemini."""
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
    )
    principles = load_triz_principles()
    principles_text = "\n".join(
        f"#{p.number} {p.name_en} ({p.name_ko}): {p.description}" for p in principles
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRIZ_CLASSIFIER_SYSTEM),
            ("human", TRIZ_CLASSIFIER_HUMAN),
        ]
    ).partial(principles_list=principles_text)

    field_context = f"기술 분야: {technical_field}" if technical_field else ""
    chain = prompt | llm
    response = await chain.ainvoke(
        {
            "problem_description": problem_description,
            "field_context": field_context,
        }
    )
    return parse_principles_response(response.content)
```

**Step 2: Run test**

Run: `pytest tests/test_triz_classifier.py -v`
Expected: PASS (tests only `parse_principles_response`, no LLM calls)

**Step 3: Commit**

```bash
git add app/services/triz_classifier.py
git commit -m "refactor: convert TRIZClassifier class to async function, swap to Gemini"
```

---

### Task 5: Update DraftGenerator to use Gemini

**Files:**
- Modify: `app/services/draft_generator.py`
- Test: `tests/test_draft_generator.py` — no changes needed (tests `export_to_docx`, no LLM)

**Step 1: Rewrite draft_generator.py**

```python
import logging
import uuid
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import Settings
from app.models.patent_draft import PatentDraft
from app.utils.docx_exporter import export_to_docx

logger = logging.getLogger(__name__)

DRAFT_SYSTEM = """당신은 한국 특허청(KIPO) 특허 명세서 작성 전문가입니다.
주어진 발명 아이디어를 바탕으로 특허 명세서의 각 섹션을 전문적으로 작성합니다.
반드시 아래 JSON 스키마를 준수하여 응답하세요."""

DRAFT_HUMAN = """발명 아이디어:
{idea}

기술적 문제:
{problem_description}

적용된 TRIZ 원리:
{triz_principles}

위 내용을 바탕으로 특허 명세서를 JSON 형식으로 작성하세요.

필수 필드:
- title: 발명의 명칭 (한국어)
- abstract: 요약 (200자 내외)
- background: 발명의 배경 (기술 분야 및 선행 기술 문제점)
- problem_statement: 해결하려는 과제
- solution: 과제의 해결 수단 (구체적인 기술 구현)
- claims: 청구항 배열 (독립항 1개 + 종속항 2개 이상)
- effects: 발명의 효과"""


async def generate_draft(
    idea: str,
    problem_description: str,
    triz_principles_text: str,
    settings: Settings,
) -> tuple[PatentDraft, str | None]:
    """Generate a structured patent draft + DOCX using Gemini."""
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
    ).with_structured_output(PatentDraft)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", DRAFT_SYSTEM),
            ("human", DRAFT_HUMAN),
        ]
    )
    chain = prompt | llm
    draft = await chain.ainvoke(
        {
            "idea": idea,
            "problem_description": problem_description,
            "triz_principles": triz_principles_text,
        }
    )

    # Export to DOCX
    output_dir = Path("data/drafts")
    output_dir.mkdir(parents=True, exist_ok=True)
    docx_path = None
    try:
        filename = f"patent_draft_{uuid.uuid4().hex[:8]}.docx"
        docx_path = str(output_dir / filename)
        export_to_docx(draft, docx_path)
        logger.info(f"DOCX exported to {docx_path}")
    except Exception as e:
        logger.error(f"Failed to export DOCX: {e}")

    return draft, docx_path
```

**Step 2: Run test**

Run: `pytest tests/test_draft_generator.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add app/services/draft_generator.py
git commit -m "refactor: convert DraftGenerator class to async function, swap to Gemini"
```

---

### Task 6: Add CRAG-aware PatentSearcher

**Files:**
- Modify: `app/services/patent_searcher.py`
- Test: `tests/test_patent_searcher.py` — existing tests still pass (test `merge_and_score_results`)

The PatentSearcher keeps its hybrid search logic. We add no CRAG logic here — that lives in the graph nodes. But we refactor to a function-based API consistent with other services.

**Step 1: Rewrite patent_searcher.py**

Keep `merge_and_score_results` unchanged. Convert `PatentSearcher` class to keep it (the graph node will instantiate it). The key change: keep the class but remove `__init__` dependency on the full Settings for testability:

```python
import logging

from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import CrossEncoder

from app.config import Settings
from app.models.patent_draft import SimilarPatent

logger = logging.getLogger(__name__)


def merge_and_score_results(docs: list[Document], scores: list[float]) -> list[SimilarPatent]:
    if not docs:
        return []
    results = []
    for doc, score in zip(docs, scores):
        results.append(
            SimilarPatent(
                title=doc.metadata.get("title", ""),
                abstract=doc.page_content,
                application_number=doc.metadata.get("application_number", ""),
                similarity_score=round(score, 4),
            )
        )
    return results


class PatentSearcher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def _get_vectorstore(self) -> Chroma:
        return Chroma(
            persist_directory=self.settings.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings,
            collection_name="patents",
        )

    async def search(self, query: str, top_k: int | None = None) -> list[SimilarPatent]:
        top_k = top_k or self.settings.RERANK_TOP_K
        retrieval_k = self.settings.RETRIEVAL_TOP_K

        vectorstore = self._get_vectorstore()
        collection = vectorstore._collection
        if collection.count() == 0:
            logger.warning("ChromaDB is empty. Run the ingestion script first.")
            return []

        # Dense retriever (vector search)
        dense_retriever = vectorstore.as_retriever(search_kwargs={"k": retrieval_k})

        # Sparse retriever (BM25)
        all_docs = vectorstore.get()
        if not all_docs["documents"]:
            return []

        bm25_docs = [
            Document(page_content=doc, metadata=meta)
            for doc, meta in zip(all_docs["documents"], all_docs["metadatas"])
        ]
        sparse_retriever = BM25Retriever.from_documents(bm25_docs, k=retrieval_k)

        # Retrieve candidates — use dense only to avoid import issues
        candidates = await dense_retriever.ainvoke(query)

        # Add BM25 results
        bm25_results = sparse_retriever.invoke(query)
        candidates.extend(bm25_results)

        if not candidates:
            return []

        # Deduplicate by content
        seen = set()
        unique_candidates = []
        for doc in candidates:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_candidates.append(doc)

        # Cross-Encoder reranking
        pairs = [[query, doc.page_content] for doc in unique_candidates]
        scores = self.reranker.predict(pairs).tolist()

        # Sort by score descending, take top_k
        scored = sorted(zip(unique_candidates, scores), key=lambda x: x[1], reverse=True)
        top_docs = [doc for doc, _ in scored[:top_k]]
        top_scores = [score for _, score in scored[:top_k]]

        # Normalize scores to 0-1 range
        max_score = max(top_scores) if top_scores else 1.0
        min_score = min(top_scores) if top_scores else 0.0
        score_range = max_score - min_score if max_score != min_score else 1.0
        normalized_scores = [(s - min_score) / score_range for s in top_scores]

        return merge_and_score_results(top_docs, normalized_scores)
```

Note: The original code imported `EnsembleRetriever` from `langchain_classic.retrievers` which may not be installed. We switch to manual merging (dense + BM25 concat + dedup) which is simpler and avoids the dependency.

**Step 2: Run test**

Run: `pytest tests/test_patent_searcher.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add app/services/patent_searcher.py
git commit -m "refactor: simplify PatentSearcher hybrid retrieval, drop EnsembleRetriever"
```

---

### Task 7: Build the full LangGraph pipeline (ReasoningAgent rewrite)

This is the core task. The new `ReasoningAgent` contains all 8 nodes and replaces the old 5-node graph.

**Files:**
- Rewrite: `app/services/reasoning_agent.py`
- Rewrite: `tests/test_reasoning_agent.py`

**Step 1: Write the failing test**

Rewrite `tests/test_reasoning_agent.py`:

```python
import json
from unittest.mock import AsyncMock, MagicMock, patch


def test_route_after_evaluate_novelty_novel():
    """Should route to draft_patent when idea is novel."""
    from app.services.reasoning_agent import route_after_evaluate_novelty

    state = {"novelty_score": 0.8, "evasion_count": 0}
    result = route_after_evaluate_novelty(state, threshold=0.5, max_attempts=3)
    assert result == "draft_patent"


def test_route_after_evaluate_novelty_not_novel():
    """Should route to evade when idea is not novel and attempts remain."""
    from app.services.reasoning_agent import route_after_evaluate_novelty

    state = {"novelty_score": 0.3, "evasion_count": 0}
    result = route_after_evaluate_novelty(state, threshold=0.5, max_attempts=3)
    assert result == "evade"


def test_route_after_evaluate_novelty_max_attempts():
    """Should route to draft_patent when max attempts reached even if not novel."""
    from app.services.reasoning_agent import route_after_evaluate_novelty

    state = {"novelty_score": 0.3, "evasion_count": 3}
    result = route_after_evaluate_novelty(state, threshold=0.5, max_attempts=3)
    assert result == "draft_patent"


def test_route_after_evaluate_context_sufficient():
    """Should route to generate_idea when context is sufficient."""
    from app.services.reasoning_agent import route_after_evaluate_context

    state = {"context_sufficient": True}
    assert route_after_evaluate_context(state) == "generate_idea"


def test_route_after_evaluate_context_insufficient():
    """Should route to search_kipris when context is insufficient."""
    from app.services.reasoning_agent import route_after_evaluate_context

    state = {"context_sufficient": False}
    assert route_after_evaluate_context(state) == "search_kipris"
```

**Step 2: Rewrite app/services/reasoning_agent.py**

```python
import json
import logging
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from app.config import Settings
from app.models.state import AgentState
from app.prompts.crag import CRAG_EVALUATION_HUMAN, CRAG_EVALUATION_SYSTEM
from app.prompts.evasion import EVASION_HUMAN, EVASION_SYSTEM
from app.prompts.novelty import NOVELTY_EVALUATION_HUMAN, NOVELTY_EVALUATION_SYSTEM
from app.prompts.triz_expert import TRIZ_EXPERT_SYSTEM, TRIZ_IDEA_GENERATION_HUMAN
from app.services.patent_searcher import PatentSearcher
from app.services.triz_classifier import classify_triz, parse_principles_response
from app.utils.kipris_client import KIPRISClient

logger = logging.getLogger(__name__)


def route_after_evaluate_novelty(
    state: dict[str, Any], threshold: float, max_attempts: int
) -> str:
    """Route after novelty evaluation: novel → draft, not novel → evade or draft."""
    if state["novelty_score"] >= threshold:
        return "draft_patent"
    if state["evasion_count"] >= max_attempts:
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
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,
        )
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
                max_attempts=self.settings.MAX_EVASION_ATTEMPTS,
            ),
            {"draft_patent": "draft_patent", "evade": "evade"},
        )
        graph.add_edge("evade", "search_internal")
        graph.add_edge("draft_patent", END)

        return graph.compile()

    # ── Node implementations ──────────────────────────────────────

    async def _classify_triz_node(self, state: AgentState) -> dict:
        principles = await classify_triz(
            state["user_problem"], state["technical_field"], self.settings
        )
        return {
            "triz_principles": principles,
            "current_step": "classify_triz",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[TRIZ 분류] {len(principles)}개 원리 선정"],
        }

    async def _search_internal_node(self, state: AgentState) -> dict:
        query = state["user_problem"]
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
        keyword = state["user_problem"][:50]
        patents = await self.kipris_client.search_patents(keyword, num_of_rows=20)
        return {
            "current_step": "search_kipris",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[KIPRIS 검색] 외부 API에서 {len(patents)}건 추가 수집"],
        }

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
            "current_step": "generate_idea",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[아이디어 생성] TRIZ 원리 {triz_text} 적용"],
        }

    async def _evaluate_novelty_node(self, state: AgentState) -> dict:
        patents_text = "\n".join(
            f"- {p.title} (유사도: {p.similarity_score:.1%}): {p.abstract[:150]}"
            for p in state["similar_patents"][:5]
        )
        if not patents_text:
            patents_text = "(선행기술 없음)"

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
            is_novel = data.get("is_novel", novelty_score >= 0.5)
        except (json.JSONDecodeError, AttributeError, ValueError):
            novelty_score = 0.5
            reasoning = "평가 파싱 실패, 기본값 사용"
            is_novel = True

        status = "독창적" if is_novel else "유사"
        return {
            "novelty_score": novelty_score,
            "novelty_reasoning": reasoning,
            "current_step": "evaluate_novelty",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[신규성 평가] 점수: {novelty_score:.1%} → {status}"],
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
            "current_step": "evade",
            "reasoning_trace": state["reasoning_trace"]
            + [f"[회피 설계 #{new_count}] 새로운 아이디어 생성"],
        }

    async def _draft_patent_node(self, state: AgentState) -> dict:
        from app.services.draft_generator import generate_draft

        triz_text = ", ".join(
            f"#{p.number} {p.name_ko}({p.name_en})" for p in state["triz_principles"]
        )
        draft, docx_path = await generate_draft(
            idea=state["current_idea"],
            problem_description=state["user_problem"],
            triz_principles_text=triz_text,
            settings=self.settings,
        )
        return {
            "final_idea": state["current_idea"],
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
```

**Step 3: Run test**

Run: `pytest tests/test_reasoning_agent.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add app/services/reasoning_agent.py tests/test_reasoning_agent.py
git commit -m "feat: rewrite pipeline as all-in-LangGraph with CRAG + novelty nodes"
```

---

### Task 8: Simplify PatentService to thin wrapper

**Files:**
- Rewrite: `app/services/patent_service.py`
- Modify: `tests/test_patent_service.py`

**Step 1: Rewrite patent_service.py**

```python
import logging

from app.api.schemas.response import PatentGenerateResponse
from app.config import Settings
from app.models.state import AgentState
from app.services.reasoning_agent import PatentPipeline

logger = logging.getLogger(__name__)


class PatentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pipeline = PatentPipeline(settings)

    async def generate(
        self,
        problem_description: str,
        technical_field: str | None = None,
        max_evasion_attempts: int = 3,
    ) -> PatentGenerateResponse:
        initial_state: AgentState = {
            "user_problem": problem_description,
            "technical_field": technical_field or "",
            "triz_principles": [],
            "current_idea": "",
            "similar_patents": [],
            "max_similarity_score": 0.0,
            "novelty_score": 0.0,
            "novelty_reasoning": "",
            "context_sufficient": False,
            "evasion_count": 0,
            "final_idea": "",
            "reasoning_trace": [],
            "current_step": "",
        }

        original_max = self.settings.MAX_EVASION_ATTEMPTS
        self.settings.MAX_EVASION_ATTEMPTS = max_evasion_attempts
        try:
            final_state = await self.pipeline.run(initial_state)
        finally:
            self.settings.MAX_EVASION_ATTEMPTS = original_max

        # Reconstruct draft from final state for response
        from app.services.draft_generator import generate_draft

        triz_text = ", ".join(
            f"#{p.number} {p.name_ko}({p.name_en})"
            for p in final_state["triz_principles"]
        )
        draft, docx_path = await generate_draft(
            idea=final_state["final_idea"],
            problem_description=problem_description,
            triz_principles_text=triz_text,
            settings=self.settings,
        )

        return PatentGenerateResponse(
            patent_draft=draft,
            triz_principles=final_state["triz_principles"],
            similar_patents=final_state["similar_patents"],
            reasoning_trace=final_state["reasoning_trace"],
            docx_download_url=docx_path,
        )
```

**Step 2: Update test**

Rewrite `tests/test_patent_service.py`:

```python
def test_patent_service_has_required_methods():
    """PatentService should expose a generate() method."""
    import inspect

    from app.services.patent_service import PatentService

    assert hasattr(PatentService, "generate")
    sig = inspect.signature(PatentService.generate)
    params = list(sig.parameters.keys())
    assert "problem_description" in params
```

This test stays the same — it only checks the method signature exists.

**Step 3: Run test**

Run: `pytest tests/test_patent_service.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add app/services/patent_service.py tests/test_patent_service.py
git commit -m "refactor: simplify PatentService to thin wrapper over PatentPipeline"
```

---

### Task 9: Add SSE streaming endpoint

**Files:**
- Modify: `app/api/routes/patent.py`
- Modify: `tests/test_patent_route.py`

**Step 1: Update patent.py to add /generate/stream**

```python
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from app.api.schemas.request import PatentGenerateRequest, PatentSearchRequest
from app.api.schemas.response import PatentGenerateResponse, PatentSearchResponse
from app.config import Settings, get_settings
from app.models.state import AgentState
from app.services.patent_searcher import PatentSearcher
from app.services.patent_service import PatentService
from app.services.reasoning_agent import PatentPipeline

router = APIRouter(prefix="/patent")


def get_patent_service(settings: Settings = Depends(get_settings)) -> PatentService:
    return PatentService(settings)


def get_patent_searcher(settings: Settings = Depends(get_settings)) -> PatentSearcher:
    return PatentSearcher(settings)


def get_pipeline(settings: Settings = Depends(get_settings)) -> PatentPipeline:
    return PatentPipeline(settings)


@router.post("/generate", response_model=PatentGenerateResponse)
async def generate_patent(
    request: PatentGenerateRequest,
    service: PatentService = Depends(get_patent_service),
):
    try:
        return await service.generate(
            problem_description=request.problem_description,
            technical_field=request.technical_field,
            max_evasion_attempts=request.max_evasion_attempts,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stream")
async def generate_patent_stream(
    request: PatentGenerateRequest,
    pipeline: PatentPipeline = Depends(get_pipeline),
):
    """SSE endpoint that streams step-by-step LangGraph state updates."""

    initial_state: AgentState = {
        "user_problem": request.problem_description,
        "technical_field": request.technical_field or "",
        "triz_principles": [],
        "current_idea": "",
        "similar_patents": [],
        "max_similarity_score": 0.0,
        "novelty_score": 0.0,
        "novelty_reasoning": "",
        "context_sufficient": False,
        "evasion_count": 0,
        "final_idea": "",
        "reasoning_trace": [],
        "current_step": "",
    }

    async def event_generator():
        async for event in pipeline.stream(initial_state):
            # LangGraph astream yields dicts keyed by node name
            for node_name, node_state in event.items():
                yield {
                    "event": "step",
                    "data": json.dumps(
                        {"step": node_name, "state": _serialize_state(node_state)},
                        ensure_ascii=False,
                    ),
                }
        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(event_generator())


def _serialize_state(state: dict) -> dict:
    """Convert state to JSON-serializable dict."""
    result = {}
    for key, value in state.items():
        if hasattr(value, "model_dump"):
            result[key] = value.model_dump()
        elif isinstance(value, list) and value and hasattr(value[0], "model_dump"):
            result[key] = [item.model_dump() for item in value]
        else:
            result[key] = value
    return result


@router.post("/search", response_model=PatentSearchResponse)
async def search_patents(
    request: PatentSearchRequest,
    searcher: PatentSearcher = Depends(get_patent_searcher),
):
    try:
        results = await searcher.search(request.query, top_k=request.top_k)
        return PatentSearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{draft_id}/docx")
async def download_docx(draft_id: str):
    docx_path = Path(f"data/drafts/{draft_id}.docx")
    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="DOCX file not found")
    return FileResponse(
        path=str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"patent_draft_{draft_id}.docx",
    )
```

**Step 2: Add streaming endpoint test to test_patent_route.py**

Append to existing tests:

```python
def test_stream_endpoint_exists():
    from app.main import app

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/patent/generate/stream",
        json={"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"},
    )
    # Without valid API keys, will get 500, but route exists (not 404/405)
    assert response.status_code in (200, 500)
```

**Step 3: Run test**

Run: `pytest tests/test_patent_route.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add app/api/routes/patent.py tests/test_patent_route.py
git commit -m "feat: add SSE streaming endpoint for step-by-step patent generation"
```

---

### Task 10: Run full test suite and fix any remaining issues

**Step 1: Run all tests**

Run: `pytest -v`
Expected: All tests PASS

**Step 2: Run linter**

Run: `ruff check .`
Expected: No errors (fix any that appear)

**Step 3: Fix any failing tests or lint issues**

Address any import errors, missing fields, or type mismatches.

**Step 4: Final commit**

```bash
git add -A
git commit -m "fix: resolve test and lint issues from refactor"
```

---

### Task 11: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update CLAUDE.md**

Update the architecture section to reflect the new pipeline, Gemini model, CRAG strategy, and SSE endpoint.

**Step 2: No commit needed** (CLAUDE.md is gitignored)
