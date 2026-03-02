import logging
from pathlib import Path

from app.api.schemas.response import PatentGenerateResponse
from app.config import Settings
from app.models.state import build_initial_state
from app.services.reasoning_agent import PatentPipeline

logger = logging.getLogger(__name__)


class PatentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pipeline = PatentPipeline(settings)

    async def generate(
        self,
        problem_description: str = "",
        keyword: str | None = None,
        technical_field: str | None = None,
        max_evasion_attempts: int = 3,
    ) -> PatentGenerateResponse:
        initial_state = build_initial_state(
            problem_description=problem_description,
            keyword=keyword or "",
            technical_field=technical_field or "",
            max_evasion_attempts=max_evasion_attempts,
        )

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
