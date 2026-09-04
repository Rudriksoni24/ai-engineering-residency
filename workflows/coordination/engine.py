from __future__ import annotations

from workflows.contracts.state import WorkflowState
from workflows.coordination.contracts import (
    CoordinationTraceEvent,
    CoordinationTraceEventType,
    CoordinatorAgent,
    WorkerResult,
)
from workflows.coordination.registry import (
    WorkerRegistry,
)


class CoordinationEngine:
    def __init__(
        self,
        coordinator: CoordinatorAgent,
        worker_registry: WorkerRegistry,
    ) -> None:
        self._coordinator = coordinator
        self._worker_registry = (
            worker_registry
        )
        self._trace: list[
            CoordinationTraceEvent
        ] = []

    @property
    def trace(
        self,
    ) -> tuple[
        CoordinationTraceEvent,
        ...
    ]:
        return tuple(self._trace)

    def run(
        self,
        state: WorkflowState,
    ) -> list[WorkerResult]:
        self._trace = []

        self._trace.append(
            CoordinationTraceEvent(
                event_type=(
                    CoordinationTraceEventType
                    .COORDINATOR_STARTED
                )
            )
        )

        delegations = (
            self._coordinator.coordinate(
                state
            )
        )

        self._trace.append(
            CoordinationTraceEvent(
                event_type=(
                    CoordinationTraceEventType
                    .COORDINATOR_COMPLETED
                )
            )
        )

        results: list[
            WorkerResult
        ] = []

        for delegation in delegations:
            self._trace.append(
                CoordinationTraceEvent(
                    event_type=(
                        CoordinationTraceEventType
                        .DELEGATION_SELECTED
                    ),
                    worker_name=(
                        delegation.worker_name
                    ),
                    task=delegation.task,
                )
            )

            worker = (
                self._worker_registry.get(
                    delegation.worker_name
                )
            )

            self._trace.append(
                CoordinationTraceEvent(
                    event_type=(
                        CoordinationTraceEventType
                        .WORKER_STARTED
                    ),
                    worker_name=worker.name,
                    task=delegation.task,
                )
            )

            result = worker.run(
                delegation.task,
                state,
            )

            if (
                result.worker_name
                != worker.name
            ):
                raise ValueError(
                    "Worker returned a result "
                    "for a different worker name."
                )

            results.append(result)

            self._trace.append(
                CoordinationTraceEvent(
                    event_type=(
                        CoordinationTraceEventType
                        .WORKER_COMPLETED
                    ),
                    worker_name=worker.name,
                    task=delegation.task,
                )
            )

        state.context[
            "worker_results"
        ] = [
            {
                "worker_name": (
                    result.worker_name
                ),
                "output": result.output,
            }
            for result in results
        ]

        return results