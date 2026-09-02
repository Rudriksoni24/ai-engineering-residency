from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4


class WorkflowStatus(StrEnum):
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class WorkflowTransition:
    source: WorkflowStatus
    destination: WorkflowStatus


@dataclass
class WorkflowState:
    workflow_id: str
    status: WorkflowStatus
    input: dict[str, Any]
    result: Any | None = None
    error: str | None = None
    history: list[WorkflowTransition] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        workflow_input: dict[str, Any],
        *,
        workflow_id: str | None = None,
    ) -> WorkflowState:
        return cls(
            workflow_id=workflow_id or str(uuid4()),
            status=WorkflowStatus.CREATED,
            input=dict(workflow_input),
        )