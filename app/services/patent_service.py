import logging

from app.api.schemas.response import PatentGenerateResponse
from app.config import Settings
from app.models.state import AgentState
from app.services.draft_generator import DraftGenerator
from app.services.patent_searcher import PatentSearcher
from app.services.reasoning_agent import ReasoningAgent
from app.services.triz_classifier import TRIZClassifier

logger = logging.getLogger(__name__)


class PatentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.triz_classifier = TRIZClassifier(settings)
        self.patent_searcher = PatentSearcher(settings)
        self.reasoning_agent = ReasoningAgent(settings, self.patent_searcher)
        self.draft_generator = DraftGenerator(settings)

    async def generate(
        self,
        problem_description: str,
        technical_field: str | None = None,
        max_evasion_attempts: int = 3,
    ) -> PatentGenerateResponse:
        # Stage 1: TRIZ Classification
        logger.info("Stage 1: Classifying problem with TRIZ principles...")
        triz_principles = await self.triz_classifier.classify(problem_description, technical_field)
        if not triz_principles:
            raise ValueError("TRIZ classification failed to return any principles.")

        # Stage 2 & 3: Reasoning Agent (includes search + evasion loop)
        logger.info("Stage 2-3: Running reasoning agent with evasion loop...")
        initial_state: AgentState = {
            "user_problem": problem_description,
            "triz_principles": triz_principles,
            "current_idea": "",
            "similar_patents": [],
            "max_similarity_score": 0.0,
            "evasion_count": 0,
            "should_evade": False,
            "final_idea": "",
            "reasoning_trace": [],
        }
        # Override max evasion attempts if specified
        original_max = self.settings.MAX_EVASION_ATTEMPTS
        self.settings.MAX_EVASION_ATTEMPTS = max_evasion_attempts
        try:
            final_state = await self.reasoning_agent.run(initial_state)
        finally:
            self.settings.MAX_EVASION_ATTEMPTS = original_max

        # Stage 4: Draft Generation
        logger.info("Stage 4: Generating structured patent draft...")
        triz_text = ", ".join(f"#{p.number} {p.name_ko}({p.name_en})" for p in triz_principles)
        draft, docx_path = await self.draft_generator.generate(
            idea=final_state["final_idea"],
            problem_description=problem_description,
            triz_principles_text=triz_text,
        )

        return PatentGenerateResponse(
            patent_draft=draft,
            triz_principles=triz_principles,
            similar_patents=final_state["similar_patents"],
            reasoning_trace=final_state["reasoning_trace"],
            docx_download_url=docx_path,
        )
