from rag.evaluation.contracts import (
    EvaluationCase,
    EvaluationResult,
    MetricResult,
)
from rag.evaluation.metrics import (
    context_coverage,
    keyword_recall,
)


class RAGEvaluator:
    def evaluate(
        self,
        case: EvaluationCase,
    ) -> EvaluationResult:
        metrics = [
            MetricResult(
                name="keyword_recall",
                score=keyword_recall(
                    expected_answer=case.expected_answer,
                    generated_answer=case.generated_answer,
                ),
                details=(
                    "Measures overlap between expected "
                    "and generated answer tokens."
                ),
            ),
            MetricResult(
                name="context_coverage",
                score=context_coverage(
                    generated_answer=case.generated_answer,
                    retrieved_documents=case.retrieved_documents,
                ),
                details=(
                    "Measures how much of the generated "
                    "answer is represented in retrieved context."
                ),
            ),
        ]

        return EvaluationResult(
            case=case,
            metrics=metrics,
        )