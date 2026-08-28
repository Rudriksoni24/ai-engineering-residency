import json

from rag.evaluation.dataset import EvaluationDataset


def test_dataset_loads_cases(
    tmp_path,
):
    dataset_path = (
        tmp_path / "cases.json"
    )

    data = [
        {
            "query": "Question one",
            "expected_answer": "Answer one",
        },
        {
            "query": "Question two",
            "expected_answer": "Answer two",
        },
    ]

    dataset_path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    dataset = EvaluationDataset.from_json(
        dataset_path
    )

    assert len(dataset.cases) == 2
    assert (
        dataset.cases[0].query
        == "Question one"
    )