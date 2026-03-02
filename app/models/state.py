from typing import TypedDict

from app.models.patent_draft import PatentDraft, SimilarPatent
from app.models.triz import TRIZPrinciple


class AgentState(TypedDict):
    user_problem: str
    keyword: str
    technical_field: str
    triz_principles: list[TRIZPrinciple]
    current_idea: str
    similar_patents: list[SimilarPatent]
    max_similarity_score: float
    novelty_score: float
    novelty_reasoning: str
    context_sufficient: bool
    evasion_count: int
    max_evasion_attempts: int
    final_idea: str
    reasoning_trace: list[str]
    current_step: str
    patent_draft: PatentDraft | None
    docx_path: str | None


def build_initial_state(
    problem_description: str = "",
    keyword: str = "",
    technical_field: str = "",
    max_evasion_attempts: int = 3,
) -> AgentState:
    """Build the initial AgentState dict for a pipeline run."""
    return {
        "user_problem": problem_description,
        "keyword": keyword,
        "technical_field": technical_field,
        "triz_principles": [],
        "current_idea": "",
        "similar_patents": [],
        "max_similarity_score": 0.0,
        "novelty_score": 0.0,
        "novelty_reasoning": "",
        "context_sufficient": False,
        "evasion_count": 0,
        "max_evasion_attempts": max_evasion_attempts,
        "final_idea": "",
        "reasoning_trace": [],
        "current_step": "",
        "patent_draft": None,
        "docx_path": None,
    }
