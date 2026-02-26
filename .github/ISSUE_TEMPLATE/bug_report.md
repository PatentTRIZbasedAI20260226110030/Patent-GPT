---
name: Bug Report
about: Report a bug in Patent-GPT
title: "[BUG] "
labels: bug, needs-triage
assignees: ""
---

## Bug Description

<!-- What happened? Be as specific as possible. -->

## Steps to Reproduce

1.
2.
3.

<!-- Example:
1. Run `uvicorn app.main:app`
2. Send POST to /api/v1/patent/generate with body {...}
3. See error in response / logs
-->

## Expected Behavior

<!-- What should have happened instead? -->

## Actual Behavior

<!-- What actually happened? Include error messages if any. -->

## Error Logs / Traceback

```
(paste logs or traceback here)
```

## Environment

- **Python version:**
- **OS:**
- **Relevant packages:** (e.g., langchain==x.x.x, chromadb==x.x.x)

## Component

<!-- Which part of the system is affected? Check one. -->

- [ ] TRIZ Idea Generator (classifier, few-shot prompting)
- [ ] Patent Searcher (BM25, vector search, reranking)
- [ ] Reasoning Agent (LangGraph evasion loop)
- [ ] Draft Generator (Pydantic output, DOCX export)
- [ ] FastAPI / API Layer (routes, schemas, middleware)
- [ ] KIPRISplus Client (patent data fetching)
- [ ] Configuration / Environment (.env, pydantic-settings)
- [ ] Other

## Additional Context

<!-- Screenshots, related issues, or anything else that might help. -->
