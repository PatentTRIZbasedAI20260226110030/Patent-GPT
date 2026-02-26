#!/usr/bin/env bash
# setup_github_labels.sh — Create project-specific GitHub labels for Patent-GPT
#
# Usage:
#   chmod +x scripts/setup_github_labels.sh
#   ./scripts/setup_github_labels.sh
#
# Prerequisites:
#   - GitHub CLI (gh) installed and authenticated
#   - Run from the repo root, or set GH_REPO

set -euo pipefail

REPO="${GH_REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
echo "Configuring labels for: $REPO"

# ── Helper ──────────────────────────────────────────────
create_label() {
  local name="$1" color="$2" description="$3"
  if gh label create "$name" --repo "$REPO" --color "$color" --description "$description" 2>/dev/null; then
    echo "  ✓ Created: $name"
  else
    # Label already exists — update it
    gh label edit "$name" --repo "$REPO" --color "$color" --description "$description" 2>/dev/null \
      && echo "  ↻ Updated: $name" \
      || echo "  ✗ Failed:  $name"
  fi
}

# ── Standard Labels ─────────────────────────────────────
echo ""
echo "=== Standard Labels ==="
create_label "bug"              "d73a4a" "Something isn't working"
create_label "enhancement"      "a2eeef" "New feature or request"
create_label "documentation"    "0075ca" "Improvements or additions to documentation"
create_label "good first issue" "7057ff" "Good for newcomers"
create_label "help wanted"      "008672" "Extra attention is needed"
create_label "duplicate"        "cfd3d7" "This issue or PR already exists"
create_label "wontfix"          "ffffff" "This will not be worked on"
create_label "invalid"          "e4e669" "This doesn't seem right"
create_label "question"         "d876e3" "Further information is requested"

# ── Priority Labels ─────────────────────────────────────
echo ""
echo "=== Priority Labels ==="
create_label "priority: critical" "b60205" "Must fix immediately"
create_label "priority: high"     "d93f0b" "Should fix in current sprint"
create_label "priority: medium"   "fbca04" "Fix when possible"
create_label "priority: low"      "0e8a16" "Nice to have"

# ── Status Labels ───────────────────────────────────────
echo ""
echo "=== Status Labels ==="
create_label "needs-triage"     "ededed" "Needs initial assessment"
create_label "blocked"          "b60205" "Blocked by another issue or external dependency"
create_label "in-review"        "1d76db" "Under code review"
create_label "ready-for-dev"    "0e8a16" "Triaged and ready to pick up"

# ── AI / Project-Specific Labels ────────────────────────
echo ""
echo "=== AI / Project-Specific Labels ==="
create_label "rag-pipeline"       "5319e7" "Hybrid search, BM25, vector retrieval, reranking"
create_label "prompt-engineering"  "d4c5f9" "Prompt template design or modification"
create_label "langgraph-agent"    "f9d0c4" "LangGraph evasion loop and agent workflow"
create_label "triz-logic"         "c5def5" "TRIZ 40 principles, classification, few-shot"
create_label "eval-ragas"         "bfdadc" "RAGAS evaluation metrics and quality measurement"
create_label "ai-model-update"    "e99695" "LLM or embedding model changes"
create_label "kipris-api"         "fef2c0" "KIPRISplus patent data integration"

# ── Component Labels ────────────────────────────────────
echo ""
echo "=== Component Labels ==="
create_label "component: triz-classifier"   "c2e0c6" "Stage 1 — TRIZ Idea Generator"
create_label "component: patent-searcher"   "c2e0c6" "Stage 2 — Hybrid Patent Searcher"
create_label "component: reasoning-agent"   "c2e0c6" "Stage 3 — LangGraph Reasoning Agent"
create_label "component: draft-generator"   "c2e0c6" "Stage 4 — Patent Draft Generator"
create_label "component: api"               "c2e0c6" "FastAPI routes and schemas"
create_label "component: config"            "c2e0c6" "Configuration, environment, settings"

# ── Milestone Labels ────────────────────────────────────
echo ""
echo "=== Milestone Labels ==="
create_label "v0.1.0"  "006b75" "Foundation — scaffolding, config, models"
create_label "v0.2.0"  "006b75" "Core Services — TRIZ, KIPRISplus, search"
create_label "v0.3.0"  "006b75" "Agent & Output — LangGraph, draft gen"
create_label "v0.4.0"  "006b75" "Ship — wiring, tests, polish"

echo ""
echo "Done! Labels configured for $REPO"
