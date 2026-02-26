# Patent-GPT Wiki

Welcome to the Patent-GPT project wiki.

## Project Overview

**Patent-GPT** is an agentic RAG-based invention copilot that combines TRIZ methodology with Large Language Models. It helps users go from a vague problem or keyword to a structured, novel patent draft.

**Core Flow:** Keyword Input → TRIZ-based Idea Generation → Patent Novelty Evaluation → Evasion Design (if needed) → Structured Patent Draft

## Target Users

- **Individual Inventors** — Have a problem but lack a systematic way to turn it into a patentable idea
- **Aspiring Entrepreneurs** — Want to build a patent portfolio for business
- **R&D Engineers** — Need to quickly explore inventive design alternatives

## Quick Links

| Page | Description |
| :-- | :-- |
| [Architecture](Architecture) | System architecture: hybrid search, classifier router, LangGraph loop |
| [TRIZ Methodology](TRIZ_Methodology) | The 40 inventive principles and few-shot persona logic |

## Tech Stack

| Category | Technology |
| :-- | :-- |
| Language | Python 3.11+ |
| Framework | FastAPI |
| LLM Orchestration | LangChain, LangGraph |
| LLM | OpenAI GPT-4o (generation), GPT-4o-mini (classification) |
| Embeddings | text-embedding-3-small |
| Vector DB | ChromaDB (local) |
| Patent Data | KIPRISplus Open API |
| Search | BM25 + Cross-Encoder reranking |
| Output | Pydantic + python-docx |

## Milestones

| Version | Scope | Status |
| :-- | :-- | :--: |
| v0.1.0 | Foundation — scaffolding, config, models, API skeleton | Done |
| v0.2.0 | Core Services — TRIZ classifier, KIPRISplus, hybrid search | In Progress |
| v0.3.0 | Agent & Output — LangGraph reasoning, draft generator | Planned |
| v0.4.0 | Ship — route wiring, full tests, polish | Planned |

## Repository

- **GitHub:** [Patent-GPT](https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT)
- **Main branch:** `main`
- **Development branch:** `develop`
