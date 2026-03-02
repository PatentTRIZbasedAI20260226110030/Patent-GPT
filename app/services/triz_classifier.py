import json
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import Settings
from app.models.triz import (
    ContradictionMatrix,
    TRIZPrinciple,
    load_contradiction_matrix,
    load_triz_principles,
)
from app.prompts.classifier import TRIZ_CLASSIFIER_HUMAN, TRIZ_CLASSIFIER_SYSTEM
from app.prompts.parameter_extractor import (
    PARAM_EXTRACTION_HUMAN,
    PARAM_EXTRACTION_SYSTEM,
)

logger = logging.getLogger(__name__)


def parse_principles_response(content: str) -> list[TRIZPrinciple]:
    try:
        data = json.loads(content)
        return [TRIZPrinciple(**item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse TRIZ classifier response: {e}")
        return []


async def _extract_contradiction_params(
    problem_description: str,
    technical_field: str,
    matrix: ContradictionMatrix,
    llm: ChatGoogleGenerativeAI,
) -> tuple[int | None, int | None]:
    """Extract improving/worsening engineering parameters from a problem."""
    parameter_list = "\n".join(matrix.get_parameter_names())
    prompt = ChatPromptTemplate.from_messages(
        [("system", PARAM_EXTRACTION_SYSTEM), ("human", PARAM_EXTRACTION_HUMAN)]
    ).partial(parameter_list=parameter_list)

    field_context = f"기술 분야: {technical_field}" if technical_field else ""
    chain = prompt | llm
    response = await chain.ainvoke(
        {"problem_description": problem_description, "field_context": field_context}
    )
    try:
        data = json.loads(response.content)
        improving = data.get("improving_param")
        worsening = data.get("worsening_param")
        if improving is not None and worsening is not None:
            return int(improving), int(worsening)
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"Failed to parse parameter extraction response: {e}")
    return None, None


def _build_matrix_context(
    matrix: ContradictionMatrix,
    improving: int | None,
    worsening: int | None,
    principles: list[TRIZPrinciple],
) -> str:
    """Build matrix context string for the classifier prompt."""
    if improving is None or worsening is None:
        return ""

    recommended = matrix.lookup(improving, worsening)
    if not recommended:
        return ""

    principles_map = {p.number: p for p in principles}
    names = []
    for num in recommended:
        p = principles_map.get(num)
        if p:
            names.append(f"#{num} {p.name_ko} ({p.name_en})")
        else:
            names.append(f"#{num}")

    return (
        f"\n모순 행렬 추천 원리 (개선: 파라미터 {improving}, "
        f"악화: 파라미터 {worsening}):\n"
        + ", ".join(names)
        + "\n위 원리를 우선적으로 고려하세요."
    )


async def classify_triz(
    problem_description: str,
    technical_field: str,
    settings: Settings,
    keyword: str | None = None,
) -> list[TRIZPrinciple]:
    """Classify problem into top-3 TRIZ principles.

    Routes to ML or LLM classifier based on settings.TRIZ_ROUTER.
    LLM path uses two-step process:
    1. Extract engineering parameters and look up contradiction matrix
    2. LLM selects principles guided by matrix recommendations
    """
    if settings.TRIZ_ROUTER == "ml":
        return _classify_triz_ml(problem_description, settings)

    return await _classify_triz_llm(
        problem_description, technical_field, settings, keyword
    )


def _classify_triz_ml(
    problem_description: str,
    settings: Settings,
) -> list[TRIZPrinciple]:
    """Classify using trained ML model."""
    from app.services.ml_classifier import MLTrizClassifier

    classifier = MLTrizClassifier(settings.ML_MODEL_PATH)
    return classifier.predict(problem_description, top_k=3)


async def _classify_triz_llm(
    problem_description: str,
    technical_field: str,
    settings: Settings,
    keyword: str | None = None,
) -> list[TRIZPrinciple]:
    """Classify using Gemini LLM with contradiction matrix guidance."""
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
    )
    principles = load_triz_principles()
    principles_text = "\n".join(
        f"#{p.number} {p.name_en} ({p.name_ko}): {p.description}" for p in principles
    )

    # Combine keyword and problem_description
    combined_problem = problem_description
    if keyword:
        if combined_problem:
            combined_problem = f"{combined_problem} (키워드: {keyword})"
        else:
            combined_problem = keyword

    # Step 1: Extract contradiction parameters and look up matrix
    matrix_context = ""
    try:
        matrix = load_contradiction_matrix()
        improving, worsening = await _extract_contradiction_params(
            combined_problem, technical_field, matrix, llm
        )
        matrix_context = _build_matrix_context(
            matrix, improving, worsening, principles
        )
    except FileNotFoundError:
        logger.info("Contradiction matrix not found, skipping matrix lookup")
    except Exception as e:
        logger.warning(f"Matrix lookup failed, falling back to LLM-only: {e}")

    # Step 2: LLM classification with matrix guidance
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRIZ_CLASSIFIER_SYSTEM),
            ("human", TRIZ_CLASSIFIER_HUMAN),
        ]
    ).partial(principles_list=principles_text, matrix_context=matrix_context)

    field_context = f"기술 분야: {technical_field}" if technical_field else ""
    chain = prompt | llm
    response = await chain.ainvoke(
        {
            "problem_description": combined_problem,
            "field_context": field_context,
        }
    )
    return parse_principles_response(response.content)
