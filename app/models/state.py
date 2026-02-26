from typing import TypedDict

from app.models.patent_draft import SimilarPatent
from app.models.triz import TRIZPrinciple


class AgentState(TypedDict):
    user_problem: str
    triz_principles: list[TRIZPrinciple]
    current_idea: str
    similar_patents: list[SimilarPatent]
    max_similarity_score: float
    evasion_count: int
    should_evade: bool
    final_idea: str
    reasoning_trace: list[str]
