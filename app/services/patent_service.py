import logging
from pathlib import Path

from app.api.schemas.response import PatentGenerateResponse
from app.config import Settings
from app.models.state import AgentState
from app.services.draft_generator import generate_draft
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
            "final_idea": "",
            "reasoning_trace": [],
            "current_step": "",
        }

        original_max = self.settings.MAX_EVASION_ATTEMPTS
        self.settings.MAX_EVASION_ATTEMPTS = max_evasion_attempts
        try:
            final_state = await self.pipeline.run(initial_state)
        finally:
            self.settings.MAX_EVASION_ATTEMPTS = original_max

        # Generate draft from final idea
        triz_text = ", ".join(
            f"#{p.number} {p.name_ko}({p.name_en})"
            for p in final_state["triz_principles"]
        )
        draft, docx_path = await generate_draft(
            idea=final_state["final_idea"],
            problem_description=problem_description,
            triz_principles_text=triz_text,
            settings=self.settings,
        )
        draft_id = Path(docx_path).stem if docx_path else None

        return PatentGenerateResponse(
            patent_draft=draft,
            triz_principles=final_state["triz_principles"],
            similar_patents=final_state["similar_patents"],
            reasoning_trace=final_state["reasoning_trace"],
            draft_id=draft_id,
            novelty_score=final_state.get("novelty_score"),
            threshold=self.settings.SIMILARITY_THRESHOLD,
            docx_download_url=docx_path,
        )
