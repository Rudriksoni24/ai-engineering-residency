from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    delay_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.max_attempts <= 0:
            raise ValueError(
                "max_attempts must be "
                "greater than zero."
            )

        if self.delay_seconds < 0:
            raise ValueError(
                "delay_seconds cannot "
                "be negative."
            )