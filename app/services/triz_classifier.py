import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

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


async def classify_triz(
    problem_description: str,
    technical_field: str,
    settings: Settings,
    keyword: str | None = None,
) -> list[TRIZPrinciple]:
    """Classify problem into top-3 TRIZ principles using Gemini."""
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
    )
    principles = load_triz_principles()
    principles_text = "\n".join(
        f"#{p.number} {p.name_en} ({p.name_ko}): {p.description}" for p in principles
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRIZ_CLASSIFIER_SYSTEM),
            ("human", TRIZ_CLASSIFIER_HUMAN),
        ]
    ).partial(principles_list=principles_text)

    # Combine keyword and problem_description for classification
    combined_problem = problem_description
    if keyword:
        if combined_problem:
            combined_problem = f"{combined_problem} (키워드: {keyword})"
        else:
            combined_problem = keyword

    field_context = f"기술 분야: {technical_field}" if technical_field else ""
    chain = prompt | llm
    response = await chain.ainvoke(
        {
            "problem_description": combined_problem,
            "field_context": field_context,
        }
    )
    return parse_principles_response(response.content)
