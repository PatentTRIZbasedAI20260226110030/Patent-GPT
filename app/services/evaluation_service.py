import asyncio
import logging

from ragas.dataset_schema import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics.collections import AnswerRelevancy, ContextRecall, Faithfulness

from app.config import Settings, get_llm
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
    evaluator_llm = LangchainLLMWrapper(get_llm(settings, temperature=0.0))

    sample = SingleTurnSample(
        user_input=user_problem,
        response=generated_idea,
        retrieved_contexts=retrieved_contexts,
        reference=reference,
    )

    faithfulness_metric = Faithfulness(llm=evaluator_llm)
    relevancy_metric = AnswerRelevancy(llm=evaluator_llm)
    context_recall_metric = ContextRecall(llm=evaluator_llm)

    # Score all metrics concurrently — they are independent LLM calls
    async def _score(name: str, metric) -> tuple[str, float]:
        try:
            score = await metric.single_turn_ascore(sample)
            return name, float(score) if score is not None else 0.0
        except Exception as e:
            logger.warning("RAGAS metric '%s' failed: %s", name, e)
            return name, 0.0

    results = await asyncio.gather(
        _score("faithfulness", faithfulness_metric),
        _score("answer_relevancy", relevancy_metric),
        _score("context_recall", context_recall_metric),
    )
    scores = dict(results)

    return EvaluationResult(
        faithfulness=scores["faithfulness"],
        answer_relevancy=scores["answer_relevancy"],
        context_recall=scores["context_recall"],
        passed=scores["faithfulness"] >= settings.FAITHFULNESS_THRESHOLD,
    )
