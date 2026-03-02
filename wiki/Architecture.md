# Architecture

## Overview

Patent-GPT follows a **Service Layer + LangGraph Core** architecture. FastAPI routes delegate to a service layer, where each pipeline stage is a standalone, independently testable service. LangGraph is used only for the evasion loop (Stage 3) where stateful iteration is needed.

## System Diagram

```
┌───────────────────────────────────────────────────┐
│                  FastAPI Server                    │
├───────────────────────────────────────────────────┤
│  POST /api/v1/patent/generate                     │
│                    │                              │
│                    ▼                              │
│  ┌────────────────────────────────────────────┐   │
│  │         PatentService (Orchestrator)        │   │
│  │                                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
│  │  │ Stage 1  │→ │ Stage 2  │→ │ Stage 3  │ │   │
│  │  │   TRIZ   │  │  Patent  │  │ Reasoning│ │   │
│  │  │Classifier│  │ Searcher │  │  Agent   │ │   │
│  │  └──────────┘  └──────────┘  └────┬─────┘ │   │
│  │                                   │        │   │
│  │                   ┌───────────────┘        │   │
│  │                   ▼                        │   │
│  │  similarity>80%? ─YES─→ Evasion Loop       │   │
│  │       │                   (max 3x)        │   │
│  │       NO                    │              │   │
│  │       │         ◄───────────┘              │   │
│  │       ▼                                    │   │
│  │  ┌──────────┐                              │   │
│  │  │ Stage 4  │ → JSON + DOCX               │   │
│  │  │  Draft   │                              │   │
│  │  │Generator │                              │   │
│  │  └──────────┘                              │   │
│  └────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
        │                    │
        ▼                    ▼
  ┌──────────┐        ┌───────────┐
  │ ChromaDB │        │ KIPRISplus│
  │(Vector DB)│       │  Open API │
  └──────────┘        └───────────┘
```

## 4-Stage Pipeline

### Stage 1: TRIZ Classifier

**Purpose:** Map a user's keyword or problem description to relevant TRIZ inventive principles.

- **Model:** Gemini 3.0 Flash (via `langchain-google-genai`)
- **Method:** LLM-based routing with few-shot prompting
- **Input:** Keyword + problem description + optional domain
- **Output:** List of applicable TRIZ principles with inventive idea
- **Data:** `data/triz_principles.json` (40 principles with Korean descriptions)

### Stage 2: Patent Searcher (Hybrid Search)

**Purpose:** Find existing patents similar to the generated idea to evaluate novelty.

**Retrieval strategy — three layers:**

1. **BM25 (Sparse):** Keyword-based retrieval using `rank-bm25`. Catches exact terminology matches that vector search may miss (e.g., specific patent terms like "열방출 구조체").

2. **Vector Search (Dense):** Semantic similarity via ChromaDB with `text-embedding-3-small` embeddings. Catches conceptually similar patents even when wording differs.

3. **Cross-Encoder Reranking:** `sentence-transformers` Cross-Encoder rescores the merged candidate list. Produces a final ranked list with calibrated similarity scores.

**Parameters:**
- `RETRIEVAL_TOP_K=20` — candidates from each retriever
- `RERANK_TOP_K=5` — final results after reranking

### Stage 3: Reasoning Agent (LangGraph Evasion Loop)

**Purpose:** If the top patent similarity exceeds the threshold, autonomously redesign the idea to improve novelty.

**LangGraph state machine:**

```
┌─────────────┐
│  Evaluate    │ ← receives idea + similar patents
│  Similarity  │
└──────┬──────┘
       │
       ▼
  similarity > 50%?
    │         │
   YES        NO
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│ Evade  │  │  Pass  │ → proceed to Stage 4
│ Design │  └────────┘
└───┬────┘
    │ (redesigned idea)
    │
    ▼
  attempts < 3?
    │       │
   YES      NO
    │       │
    ▼       ▼
  (loop)  ┌────────┐
          │  Pass  │ → proceed with best attempt
          └────────┘
```

- **Threshold:** `SIMILARITY_THRESHOLD=0.5`
- **Max iterations:** `MAX_EVASION_ATTEMPTS=3`
- **State:** Managed via `AgentState` TypedDict

### Stage 4: Draft Generator

**Purpose:** Produce a structured patent draft in KIPO (Korean IP Office) format.

- **Model:** Gemini 3.0 Flash with Pydantic structured output
- **Format (KIPO standard):**
  - 발명의 명칭 (Title)
  - 요약 (Abstract)
  - 청구항 (Claims)
  - 배경기술 (Background)
  - 해결과제 (Problem to Solve)
  - 해결수단 (Solution)
  - 발명의 효과 (Effects)
- **Export:** JSON response + DOCX file via `python-docx`

## Data Flow

```
User Input (keyword, problem, domain)
  │
  ▼
TRIZClassifier.classify()
  → TRIZ principles + inventive idea
  │
  ▼
PatentSearcher.search()
  → similar patents with scores
  │
  ▼
ReasoningAgent.evaluate()
  → possibly redesigned idea + novelty confirmation
  │
  ▼
DraftGenerator.generate()
  → PatentDraft (JSON) + DOCX file
```

## External Dependencies

| Service | Purpose | Auth |
| :-- | :-- | :-- |
| Google Generative AI | LLM generation (all stages) | `GOOGLE_API_KEY` |
| OpenAI API | Embeddings only (`text-embedding-3-small`) | `OPENAI_API_KEY` |
| KIPRISplus API | Korean patent data | `KIPRIS_API_KEY` |
| ChromaDB | Local vector storage | No auth (local) |
