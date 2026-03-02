import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics.collections import AnswerRelevancy, ContextRecall, Faithfulness

from app.config import Settings
from app.models.evaluation import EvaluationResult

logger = logging.getLogger(__name__)


async def evaluate_pipeline_output(
    user_problem: str,
    generated_idea: str,
    retrieved_contexts: list[str],
    reference: str,
    settings: Settings,
) -> EvaluationResult:
    """Run RAGAS evaluation on pipeline output.

    Args:
        user_problem: Original problem description from the user.
        generated_idea: The generated invention idea / patent draft text.
        retrieved_contexts: List of retrieved prior art abstracts.
        reference: Ground-truth reference (the final idea or draft abstract).
        settings: App settings with API keys and thresholds.
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.0,
    )
    evaluator_llm = LangchainLLMWrapper(llm)

    sample = SingleTurnSample(
        user_input=user_problem,
        response=generated_idea,
        retrieved_contexts=retrieved_contexts,
        reference=reference,
    )

    faithfulness_metric = Faithfulness(llm=evaluator_llm)
    relevancy_metric = AnswerRelevancy(llm=evaluator_llm)
    context_recall_metric = ContextRecall(llm=evaluator_llm)

    # Score each metric independently; catch per-metric failures
    scores: dict[str, float] = {}
    for name, metric in [
        ("faithfulness", faithfulness_metric),
        ("answer_relevancy", relevancy_metric),
        ("context_recall", context_recall_metric),
    ]:
        try:
            score = await metric.single_turn_ascore(sample)
            scores[name] = float(score) if score is not None else 0.0
        except Exception as e:
            logger.warning("RAGAS metric '%s' failed: %s", name, e)
            scores[name] = 0.0

    return EvaluationResult(
        faithfulness=scores["faithfulness"],
        answer_relevancy=scores["answer_relevancy"],
        context_recall=scores["context_recall"],
        passed=scores["faithfulness"] >= settings.FAITHFULNESS_THRESHOLD,
    )
