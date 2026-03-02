from typing import TypedDict

from app.models.patent_draft import PatentDraft, SimilarPatent
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
    max_evasion_attempts: int
    final_idea: str
    reasoning_trace: list[str]
    current_step: str
    patent_draft: PatentDraft | None
    docx_path: str | None
