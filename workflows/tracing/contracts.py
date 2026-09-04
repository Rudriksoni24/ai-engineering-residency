from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class WorkflowEventType(StrEnum):
    WORKFLOW_STARTED = "workflow_started"

    LIFECYCLE_TRANSITION = (
        "lifecycle_transition"
    )

    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"

    ROUTE_SELECTED = "route_selected"

    WORKER_DELEGATED = (
        "worker_delegated"
    )

    APPROVAL_REQUESTED = (
        "approval_requested"
    )

    APPROVAL_GRANTED = (
        "approval_granted"
    )

    APPROVAL_REJECTED = (
        "approval_rejected"
    )

    ATTEMPT_STARTED = (
        "attempt_started"
    )

    ATTEMPT_FAILED = (
        "attempt_failed"
    )

    RETRY_SCHEDULED = (
        "retry_scheduled"
    )

    WORKER_COMPLETED = (
        "worker_completed"
    )

    CHECKPOINT_SAVED = (
        "checkpoint_saved"
    )

    WORKFLOW_SUSPENDED = (
        "workflow_suspended"
    )

    WORKFLOW_COMPLETED = (
        "workflow_completed"
    )

    WORKFLOW_FAILED = (
        "workflow_failed"
    )


@dataclass(frozen=True)
class WorkflowEvent:
    event_type: WorkflowEventType
    workflow_id: str

    node: str | None = None
    worker_name: str | None = None

    source: str | None = None
    destination: str | None = None

    attempt: int | None = None

    message: str | None = None

    metadata: dict[str, Any] | None = None