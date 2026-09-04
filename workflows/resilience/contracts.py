from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RecoverableWorkflowError(
    RuntimeError
):
    pass


class RetryExhaustedError(
    RuntimeError
):
    pass


class RetryTraceEventType(StrEnum):
    ATTEMPT_STARTED = "attempt_started"
    ATTEMPT_FAILED = "attempt_failed"
    RETRY_SCHEDULED = "retry_scheduled"
    NODE_RECOVERED = "node_recovered"
    RETRY_EXHAUSTED = "retry_exhausted"
    TERMINAL_FAILURE = "terminal_failure"
    NODE_COMPLETED = "node_completed"


@dataclass(frozen=True)
class RetryTraceEvent:
    event_type: RetryTraceEventType
    node: str
    attempt: int
    error_type: str | None = None
    error_message: str | None = None