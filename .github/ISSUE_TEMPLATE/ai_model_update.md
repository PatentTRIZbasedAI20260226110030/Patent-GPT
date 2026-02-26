---
name: AI / Model Update
about: Prompt engineering, RAGAS evaluation, or agentic workflow modifications
title: "[AI] "
labels: ai-model-update
assignees: ""
---

## Update Type

<!-- What kind of AI/model change is this? Check one. -->

- [ ] **Prompt Engineering** — New or modified prompt template
- [ ] **RAGAS Evaluation** — Retrieval/generation quality measurement
- [ ] **Agentic Workflow** — LangGraph state, node, or edge changes
- [ ] **Model Configuration** — LLM/embedding model swap, parameter tuning
- [ ] **TRIZ Logic** — Changes to TRIZ principle mapping or few-shot examples
- [ ] **Retrieval Pipeline** — BM25/vector/reranking weight or strategy changes

## Description

<!-- What needs to change and why? Link to evaluation results if available. -->

## Current Behavior

<!-- How does the AI currently behave in this scenario? Include example inputs/outputs if possible. -->

**Example Input:**
```
(keyword or problem description)
```

**Current Output:**
```
(current AI response — summarize or paste)
```

## Desired Behavior

<!-- What should the AI output look like after this change? -->

**Expected Output:**
```
(desired AI response)
```

## Evaluation Plan

<!-- How will you measure whether this change is an improvement? -->

- [ ] Manual review of N sample inputs
- [ ] RAGAS metrics (faithfulness, answer relevancy, context precision)
- [ ] Similarity score comparison (before/after)
- [ ] A/B test with specific test cases
- [ ] Other:

## Affected Components

<!-- Check all pipeline stages affected by this change. -->

- [ ] `app/prompts/` — Prompt templates
- [ ] `app/services/triz_classifier.py` — TRIZ classification logic
- [ ] `app/services/patent_searcher.py` — Hybrid search / reranking
- [ ] `app/services/reasoning_agent.py` — LangGraph evasion loop
- [ ] `app/services/draft_generator.py` — Patent draft generation
- [ ] `data/triz_principles.json` — TRIZ principle definitions
- [ ] `app/config.py` — Model/threshold configuration

## Rollback Plan

<!-- If this change degrades quality, how do we revert? -->

- [ ] Revert prompt template to previous version
- [ ] Revert config parameters (document previous values below)
- [ ] Other:

**Previous parameter values (if applicable):**
| Parameter | Old Value | New Value |
| :-- | :-- | :-- |
|  |  |  |

## Additional Context

<!-- Research links, paper references, benchmark results, related issues. -->
