from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from workflows.contracts.state import WorkflowState


@dataclass(frozen=True)
class WorkflowCheckpoint:
    workflow_id: str
    state: WorkflowState
    next_node: str
    completed: bool = False


class CheckpointStore(Protocol):
    def save(
        self,
        checkpoint: WorkflowCheckpoint,
    ) -> None:
        ...

    def load(
        self,
        workflow_id: str,
    ) -> WorkflowCheckpoint | None:
        ...