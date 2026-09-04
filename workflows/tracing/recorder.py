from __future__ import annotations

from workflows.tracing.contracts import (
    WorkflowEvent,
)


class WorkflowTraceRecorder:
    def __init__(self) -> None:
        self._events: list[
            WorkflowEvent
        ] = []

    @property
    def events(
        self,
    ) -> tuple[
        WorkflowEvent,
        ...
    ]:
        return tuple(self._events)

    def record(
        self,
        event: WorkflowEvent,
    ) -> None:
        self._events.append(event)

    def clear(self) -> None:
        self._events.clear()