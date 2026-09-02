from __future__ import annotations

from workflows.contracts.state import (
    WorkflowState,
    WorkflowStatus,
    WorkflowTransition,
)


class InvalidWorkflowTransition(ValueError):
    pass


class WorkflowStateMachine:
    _ALLOWED_TRANSITIONS: dict[
        WorkflowStatus,
        frozenset[WorkflowStatus],
    ] = {  # noqa: RUF012
        WorkflowStatus.CREATED: frozenset(
            {
                WorkflowStatus.PLANNING,
            }
        ),
        WorkflowStatus.PLANNING: frozenset(
            {
                WorkflowStatus.EXECUTING,
                WorkflowStatus.FAILED,
            }
        ),
        WorkflowStatus.EXECUTING: frozenset(
            {
                WorkflowStatus.COMPLETED,
                WorkflowStatus.FAILED,
            }
        ),
        WorkflowStatus.COMPLETED: frozenset(),
        WorkflowStatus.FAILED: frozenset(),
    }

    def __init__(self, state: WorkflowState) -> None:
        self._state = state

    @property
    def state(self) -> WorkflowState:
        return self._state

    @property
    def status(self) -> WorkflowStatus:
        return self._state.status

    @property
    def history(self) -> tuple[WorkflowTransition, ...]:
        return tuple(self._state.history)

    def can_transition_to(
        self,
        destination: WorkflowStatus,
    ) -> bool:
        return destination in self._ALLOWED_TRANSITIONS[self.status]

    def transition_to(
        self,
        destination: WorkflowStatus,
    ) -> WorkflowState:
        source = self.status

        if not self.can_transition_to(destination):
            raise InvalidWorkflowTransition(
                f"Cannot transition workflow "
                f"{self._state.workflow_id!r} "
                f"from {source.value!r} "
                f"to {destination.value!r}."
            )

        transition = WorkflowTransition(
            source=source,
            destination=destination,
        )

        self._state.status = destination
        self._state.history.append(transition)

        return self._state

    def complete(self, result: object) -> WorkflowState:
        if self.status is not WorkflowStatus.EXECUTING:
            raise InvalidWorkflowTransition(
                "Workflow can only be completed while executing."
            )

        self._state.result = result
        self._state.error = None

        return self.transition_to(WorkflowStatus.COMPLETED)

    def fail(self, error: str) -> WorkflowState:
        if self.status not in {
            WorkflowStatus.PLANNING,
            WorkflowStatus.EXECUTING,
        }:
            raise InvalidWorkflowTransition(
                "Workflow can only fail while planning or executing."
            )

        self._state.error = error
        self._state.result = None

        return self.transition_to(WorkflowStatus.FAILED)