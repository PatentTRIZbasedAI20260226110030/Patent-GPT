import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.models.triz import TRIZPrinciple, load_triz_principles
from app.prompts.classifier import TRIZ_CLASSIFIER_HUMAN, TRIZ_CLASSIFIER_SYSTEM

logger = logging.getLogger(__name__)


def parse_principles_response(content: str) -> list[TRIZPrinciple]:
    try:
        data = json.loads(content)
        return [TRIZPrinciple(**item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse TRIZ classifier response: {e}")
        return []


class TRIZClassifier:
    def __init__(self, settings: Settings):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_MINI,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
        )
        self.principles = load_triz_principles()
        principles_text = "\n".join(
            f"#{p.number} {p.name_en} ({p.name_ko}): {p.description}"
            for p in self.principles
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", TRIZ_CLASSIFIER_SYSTEM),
            ("human", TRIZ_CLASSIFIER_HUMAN),
        ]).partial(principles_list=principles_text)

    async def classify(
        self, problem_description: str, technical_field: str | None = None
    ) -> list[TRIZPrinciple]:
        field_context = f"기술 분야: {technical_field}" if technical_field else ""
        chain = self.prompt | self.llm
        response = await chain.ainvoke({
            "problem_description": problem_description,
            "field_context": field_context,
        })
        return parse_principles_response(response.content)
