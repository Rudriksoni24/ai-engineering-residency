from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationCheck:
    name: str
    passed: bool
    message: str
    observed: Any = None
    expected: Any = None


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    checks: tuple[ValidationCheck, ...]
    failures: tuple[ValidationCheck, ...]
    metrics: dict[str, float] = field(
        default_factory=dict
    )

    @classmethod
    def from_checks(
        cls,
        checks: list[ValidationCheck],
        *,
        metrics: dict[str, float] | None = None,
    ) -> ValidationResult:
        failures = tuple(
            check
            for check in checks
            if not check.passed
        )

        return cls(
            passed=not failures,
            checks=tuple(checks),
            failures=failures,
            metrics=(
                dict(metrics)
                if metrics is not None
                else {}
            ),
        )