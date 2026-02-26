# Project Board Guide — Patent-GPT

Kanban board structure optimized for AI/ML development workflows.

## Board Columns

| Column | Purpose | Entry Criteria | Exit Criteria |
| :-- | :-- | :-- | :-- |
| **Backlog** | All accepted issues not yet scheduled | Issue triaged with labels | Prioritized and assigned to sprint |
| **AI Data Prep** | Data collection, embedding, prompt design, TRIZ knowledge updates | Task requires data or prompt work before coding | Data/prompts ready, reviewed by team |
| **In Progress** | Active development (coding, integration) | Developer assigned, branch created | PR opened, tests pass |
| **Eval & Review** | Code review + AI quality evaluation (RAGAS, manual checks) | PR submitted with test results | Approved by reviewer, eval metrics met |
| **Done** | Merged to `main`, deployed or ready | PR merged | — |

## Why "AI Data Prep" and "Eval & Review"?

Standard Kanban boards (To Do → In Progress → Done) miss two critical phases in AI projects:

- **AI Data Prep** captures work that isn't code yet: curating few-shot examples for TRIZ classification, tuning BM25/vector weights, designing prompt templates, preparing patent datasets for ChromaDB ingestion. Without this column, data work gets hidden inside "In Progress."

- **Eval & Review** separates code review from AI quality evaluation. A PR might pass code review but degrade retrieval quality. This column ensures RAGAS metrics, similarity scores, or manual spot-checks happen before merge.

## Setup via GitHub CLI

### 1. Create the project

```bash
# Create a new GitHub Project (v2)
gh project create \
  --owner "PatentTRIZbasedAI20260226110030" \
  --title "Patent-GPT Development" \
  --format board

# Note the project number from the output (e.g., 1)
PROJECT_NUM=1
OWNER="PatentTRIZbasedAI20260226110030"
```

### 2. Configure columns (Status field)

GitHub Projects v2 uses a "Status" field. The default values are "Todo", "In Progress", and "Done." We need to customize them.

```bash
# List the project fields to find the Status field ID
gh project field-list $PROJECT_NUM --owner $OWNER --format json

# Update the Status field options via the GitHub web UI:
#   Project → Settings → Status field → Edit options
#
# Set the following values (in order):
#   1. Backlog
#   2. AI Data Prep
#   3. In Progress
#   4. Eval & Review
#   5. Done
#
# Note: GitHub CLI does not yet support editing single-select field
# options directly. Use the web UI for this step.
```

### 3. Add existing issues to the project

```bash
# Add all open issues to the project
gh issue list --repo $OWNER/Patent-GPT --state open --json number -q '.[].number' | \
  while read -r num; do
    gh project item-add $PROJECT_NUM --owner $OWNER --url "https://github.com/$OWNER/Patent-GPT/issues/$num"
    echo "Added issue #$num"
  done
```

### 4. Create project views (optional)

```bash
# Views are configured via the web UI:
#   - "Board" view (default) — Kanban with all columns
#   - "Sprint" view — filter by milestone label (e.g., v0.2.0)
#   - "AI Work" view — filter by labels: prompt-engineering, triz-logic, eval-ragas, rag-pipeline
```

## Workflow Rules

| Rule | Description |
| :-- | :-- |
| **WIP Limits** | Max 2 items per person in "In Progress" |
| **AI Prep required** | Issues labeled `prompt-engineering`, `triz-logic`, or `rag-pipeline` must pass through "AI Data Prep" |
| **Eval gate** | Issues labeled `eval-ragas` or `ai-model-update` require documented evaluation results before leaving "Eval & Review" |
| **PR links** | Every item in "Eval & Review" must have a linked PR |

## Label → Column Mapping Guide

| Label | Starting Column |
| :-- | :-- |
| `bug`, `enhancement` (code-only) | Backlog → In Progress |
| `prompt-engineering`, `triz-logic` | Backlog → AI Data Prep → In Progress |
| `rag-pipeline`, `eval-ragas` | Backlog → AI Data Prep → In Progress |
| `documentation` | Backlog → In Progress |
| `ai-model-update` | Backlog → AI Data Prep → In Progress (must go through Eval) |
