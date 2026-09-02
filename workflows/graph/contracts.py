from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from workflows.contracts.state import WorkflowState

WorkflowNodeHandler = Callable[[WorkflowState], WorkflowState]
WorkflowRouter = Callable[[WorkflowState], str]


@dataclass(frozen=True)
class WorkflowNode:
    name: str
    handler: WorkflowNodeHandler


@dataclass(frozen=True)
class WorkflowEdge:
    source: str
    destination: str


@dataclass(frozen=True)
class ConditionalWorkflowEdge:
    source: str
    router: WorkflowRouter
    routes: dict[str, str]


class WorkflowTraceEventType(StrEnum):
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    ROUTE_SELECTED = "route_selected"
    WORKFLOW_COMPLETED = "workflow_completed"


@dataclass(frozen=True)
class WorkflowTraceEvent:
    event_type: WorkflowTraceEventType
    node: str | None = None
    source: str | None = None
    destination: str | None = None
    route: str | None = None