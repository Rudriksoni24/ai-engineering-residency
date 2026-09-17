"""Run the Day 5 workflow directly without Airflow."""

from __future__ import annotations

from pathlib import Path

from streaming.orchestration.pipeline import (
    generate_report,
    generate_transactions,
    process_transactions,
    validate_transactions,
)


def main() -> None:
    root = Path(
        "artifacts/sprint09/day05/manual"
    )

    raw_path = root / "transactions.json"
    validated_path = root / "validated.json"
    summary_path = root / "account_summary.json"
    report_path = root / "workflow_report.json"

    print("1. Generating transactions")

    generate_transactions(
        raw_path,
        count=20,
        seed=42,
    )

    print("2. Validating transactions")

    validate_transactions(
        raw_path,
        validated_path,
    )

    print("3. Running Spark processing")

    process_transactions(
        validated_path,
        summary_path,
    )

    print("4. Generating report")

    generate_report(
        summary_path,
        report_path,
    )

    print("\nWorkflow completed.")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()

    #uv run python -m streaming.scripts.run_batch_workflow 