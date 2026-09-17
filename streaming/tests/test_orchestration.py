from __future__ import annotations

import json
from pathlib import Path

import pytest

from streaming.orchestration.pipeline import (
    generate_report,
    generate_transactions,
    process_transactions,
    validate_transactions,
)


def test_generate_transactions(
    tmp_path: Path,
) -> None:
    output = tmp_path / "transactions.json"

    generate_transactions(
        output,
        count=5,
        seed=42,
    )

    payload = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert len(payload) == 5

    assert payload[0]["transaction_id"]
    assert payload[0]["account_id"]
    assert payload[0]["timestamp"]


def test_generation_is_deterministic(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    generate_transactions(
        first,
        count=5,
        seed=42,
    )

    generate_transactions(
        second,
        count=5,
        seed=42,
    )

    assert (
        json.loads(first.read_text())
        == json.loads(second.read_text())
    )


def test_validation_rejects_missing_field(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"

    input_path.write_text(
        json.dumps(
            [
                {
                    "transaction_id": "txn-001",
                }
            ]
        )
    )

    with pytest.raises(
        ValueError,
        match="missing fields",
    ):
        validate_transactions(
            input_path,
            output_path,
        )


def test_validation_rejects_negative_amount(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"

    input_path.write_text(
        json.dumps(
            [
                {
                    "transaction_id": "txn-001",
                    "account_id": "acc-001",
                    "amount": -100.0,
                    "currency": "INR",
                    "merchant_category": "grocery",
                    "transaction_type": "purchase",
                    "timestamp": (
                        "2026-09-17T08:00:00+00:00"
                    ),
                    "country": "IN",
                    "device_id": "device-001",
                }
            ]
        )
    )

    with pytest.raises(
        ValueError,
        match="amount must be positive",
    ):
        validate_transactions(
            input_path,
            output_path,
        )


def test_validate_generated_transactions(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw.json"
    validated = tmp_path / "validated.json"

    generate_transactions(
        raw,
        count=5,
        seed=42,
    )

    validate_transactions(
        raw,
        validated,
    )

    payload = json.loads(
        validated.read_text()
    )

    assert len(payload) == 5


def test_spark_processing(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw.json"
    validated = tmp_path / "validated.json"
    summary = tmp_path / "summary.json"

    generate_transactions(
        raw,
        count=5,
        seed=42,
    )

    validate_transactions(
        raw,
        validated,
    )

    process_transactions(
        validated,
        summary,
    )

    payload = json.loads(
        summary.read_text()
    )

    assert payload

    transaction_count = sum(
        row["transaction_count"]
        for row in payload
    )

    assert transaction_count == 5


def test_report_generation(
    tmp_path: Path,
) -> None:
    summary = tmp_path / "summary.json"
    report = tmp_path / "report.json"

    summary.write_text(
        json.dumps(
            [
                {
                    "account_id": "acc-001",
                    "transaction_count": 2,
                    "total_amount": 300.0,
                    "average_amount": 150.0,
                    "max_amount": 200.0,
                },
                {
                    "account_id": "acc-002",
                    "transaction_count": 1,
                    "total_amount": 500.0,
                    "average_amount": 500.0,
                    "max_amount": 500.0,
                },
            ]
        )
    )

    generate_report(
        summary,
        report,
    )

    payload = json.loads(
        report.read_text()
    )

    assert payload["status"] == "completed"
    assert payload["account_count"] == 2
    assert payload["transaction_count"] == 3
    assert payload["total_amount"] == 800.0