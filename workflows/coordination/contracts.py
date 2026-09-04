from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol

from workflows.contracts.state import WorkflowState


@dataclass(frozen=True)
class DelegationRequest:
    worker_name: str
    task: str


@dataclass(frozen=True)
class WorkerResult:
    worker_name: str
    output: Any


class WorkerAgent(Protocol):
    @property
    def name(self) -> str:
        ...

    def run(
        self,
        task: str,
        state: WorkflowState,
    ) -> WorkerResult:
        ...


class CoordinatorAgent(Protocol):
    def coordinate(
        self,
        state: WorkflowState,
    ) -> list[DelegationRequest]:
        ...


class CoordinationTraceEventType(StrEnum):
    COORDINATOR_STARTED = "coordinator_started"
    COORDINATOR_COMPLETED = "coordinator_completed"
    DELEGATION_SELECTED = "delegation_selected"
    WORKER_STARTED = "worker_started"
    WORKER_COMPLETED = "worker_completed"


@dataclass(frozen=True)
class CoordinationTraceEvent:
    event_type: CoordinationTraceEventType
    worker_name: str | None = None
    task: str | None = None