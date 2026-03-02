import logging
from pathlib import Path

from app.api.schemas.response import PatentGenerateResponse
from app.config import Settings
from app.models.state import AgentState
from app.services.reasoning_agent import PatentPipeline

logger = logging.getLogger(__name__)


class PatentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pipeline = PatentPipeline(settings)

    async def generate(
        self,
        problem_description: str,
        technical_field: str | None = None,
        max_evasion_attempts: int = 3,
    ) -> PatentGenerateResponse:
        initial_state: AgentState = {
            "user_problem": problem_description,
            "technical_field": technical_field or "",
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

        final_state = await self.pipeline.run(initial_state)

        docx_path = final_state.get("docx_path")
        draft_id = Path(docx_path).stem if docx_path else None

        return PatentGenerateResponse(
            patent_draft=final_state["patent_draft"],
            triz_principles=final_state["triz_principles"],
            similar_patents=final_state["similar_patents"],
            reasoning_trace=final_state["reasoning_trace"],
            draft_id=draft_id,
            novelty_score=final_state.get("novelty_score"),
            threshold=self.settings.SIMILARITY_THRESHOLD,
            docx_download_url=f"/api/v1/patent/{draft_id}/docx" if draft_id else None,
        )
