import json
from pathlib import Path

from rag.evaluation.contracts import EvaluationCase


class EvaluationDataset:
    def __init__(
        self,
        cases: list[EvaluationCase],
    ) -> None:
        self.cases = cases

    @classmethod
    def from_json(
        cls,
        path: str | Path,
    ) -> "EvaluationDataset":
        path = Path(path)

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        cases = [
            EvaluationCase(
                query=item["query"],
                expected_answer=item["expected_answer"],
                retrieved_documents=[],
                generated_answer="",
            )
            for item in data
        ]

        return cls(cases)