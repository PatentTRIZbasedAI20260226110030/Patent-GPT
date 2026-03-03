# TASKBOARD

> Last updated: 2026-03-03
> Assignees: **PJ** (human) · **Claude** (AI)

---

## v0.6.0 — Integration (Complete)

| # | Task | Status | Assignee | Notes |
|---|------|--------|----------|-------|
| 32 | E2E integration test — full SSE pipeline flow | `DONE` | Claude | component: api |
| 33 | Frontend SSE error handling and retry UX | `DONE` | Claude | enhancement |
| 34 | CORS and environment config for frontend-backend E2E | `DONE` | Claude | component: config |
| 35 | Documentation sync — README, CLAUDE.md, wiki | `DONE` | Claude | documentation |

## v0.7.0 — Intelligence (Complete)

| # | Task | Status | Assignee | Notes |
|---|------|--------|----------|-------|
| 21 | RAGAS Evaluation Pipeline — Faithfulness, Relevancy, Context Recall | `DONE` | Claude | PR #38 merged |
| 22 | TRIZ Contradiction Matrix — data file + classification integration | `DONE` | Claude | PR #37 merged |
| 23 | Conversation Memory — stateful multi-turn sessions | `DONE` | Claude | PR #39 merged |
| 24 | Add keyword field to PatentGenerateRequest | `DONE` | Claude | PR #36 merged |
| 25 | ML Classifier swap-in for TRIZ routing | `DONE` | Claude | PR #40 merged |

## v0.8.0 — Polish & Demo Prep (Planned)

| # | Task | Status | Assignee | Notes |
|---|------|--------|----------|-------|
| — | (awaiting planning) | `TODO` | — | presentation: 2026-03-04 |

## Completed

| # | Task | Completed | Assignee |
|---|------|-----------|----------|
| — | Windows setup guide in README.ko.md + Dependabot config | 2026-03-03 | Claude |
| — | Expand Korean TRIZ training data (~115 examples) | 2026-03-03 | PJ/Claude |
| — | Unify LLM provider to OpenAI GPT-4o-mini | 2026-03-02 | Claude |
| — | TRIZ training data pipeline + XGBoost tuning | 2026-03-02 | Claude |
| — | Simplify READMEs for demo readiness | 2026-03-02 | Claude |
| — | Wiki sync (Gemini→OpenAI, milestones) | 2026-03-02 | Claude |
| 25 | ML Classifier swap-in for TRIZ routing | 2026-03-02 | Claude |
| 23 | Conversation Memory — stateful multi-turn sessions | 2026-03-02 | Claude |
| 21 | RAGAS Evaluation Pipeline | 2026-03-02 | Claude |
| 22 | TRIZ Contradiction Matrix | 2026-03-02 | Claude |
| 24 | Add keyword field to PatentGenerateRequest | 2026-03-02 | Claude |
| 32 | E2E integration test — full SSE pipeline flow | 2026-03-02 | Claude |
| 33 | Frontend SSE error handling and retry UX | 2026-03-02 | Claude |
| 34 | CORS and environment config for frontend-backend E2E | 2026-03-02 | Claude |
| 35 | Documentation sync — README, CLAUDE.md, wiki | 2026-03-02 | Claude |
| — | Merge `main` → `develop` (wireframe files) | 2026-03-02 | Claude |
| — | GitHub sync (milestones, labels, wiki, project board) | 2026-03-02 | Claude |

---

### Status Key

- `TODO` — Not started
- `IN PROGRESS` — Actively being worked on
- `IN REVIEW` — Done, awaiting review
- `DONE` — Complete
- `BLOCKED` — Waiting on dependency

### How This Board Works

- **Claude** updates this file in real-time as tasks are picked up, progressed, or completed
- **#** column links to GitHub issue numbers
- Ad-hoc tasks (not tied to a GitHub issue) use `—` for the issue number
