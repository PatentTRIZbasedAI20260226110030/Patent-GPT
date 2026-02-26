# Patent-GPT

Agentic RAG-based invention copilot combining TRIZ methodology with LLMs.

## Features

- **TRIZ Classification** — LLM routes technical problems to the most relevant TRIZ inventive principles
- **Hybrid Patent Search** — BM25 + vector search with Cross-Encoder reranking
- **Evasion Loop** — LangGraph state machine that redesigns when similarity > 80%
- **Structured Draft** — Pydantic-validated patent specification + DOCX export (KIPO format)

## Architecture

```
Problem → TRIZClassifier → PatentSearcher → ReasoningAgent → DraftGenerator → DOCX
                              ↑                    ↓
                              └── evasion loop ────┘
```

## Quick Start

```bash
# 1. Create venv (Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and KIPRIS_API_KEY

# 4. Run tests
pytest tests/ -v

# 5. Start server
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/patent/generate` | Generate patent draft |
| POST | `/api/v1/patent/search` | Search similar patents |
| GET | `/api/v1/patent/{id}/docx` | Download DOCX draft |
| POST | `/api/v1/admin/ingest` | Ingest patents from KIPRIS |

## Tech Stack

- **Framework:** FastAPI
- **LLM:** OpenAI GPT-4o / GPT-4o-mini
- **Embeddings:** text-embedding-3-small
- **Vector DB:** ChromaDB
- **Agent:** LangGraph StateGraph
- **Patent Data:** KIPRISplus Open API
