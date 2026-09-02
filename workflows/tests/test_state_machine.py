import pytest

from workflows.contracts.state import WorkflowState, WorkflowStatus
from workflows.core.state_machine import (
    InvalidWorkflowTransition,
    WorkflowStateMachine,
)


def make_machine() -> WorkflowStateMachine:
    state = WorkflowState.create(
        {"task": "test workflow"},
        workflow_id="workflow-test-001",
    )
    return WorkflowStateMachine(state)


def test_workflow_starts_in_created_state() -> None:
    machine = make_machine()

    assert machine.status is WorkflowStatus.CREATED
    assert machine.history == ()


def test_created_can_transition_to_planning() -> None:
    machine = make_machine()

    state = machine.transition_to(WorkflowStatus.PLANNING)

    assert state.status is WorkflowStatus.PLANNING
    assert machine.status is WorkflowStatus.PLANNING


def test_workflow_can_follow_success_path() -> None:
    machine = make_machine()

    machine.transition_to(WorkflowStatus.PLANNING)
    machine.transition_to(WorkflowStatus.EXECUTING)
    machine.complete({"status": "ok"})

    assert machine.status is WorkflowStatus.COMPLETED
    assert machine.state.result == {"status": "ok"}
    assert machine.state.error is None


def test_transition_history_is_recorded() -> None:
    machine = make_machine()

    machine.transition_to(WorkflowStatus.PLANNING)
    machine.transition_to(WorkflowStatus.EXECUTING)
    machine.complete("done")

    history = machine.history

    assert len(history) == 3

    assert history[0].source is WorkflowStatus.CREATED
    assert history[0].destination is WorkflowStatus.PLANNING

    assert history[1].source is WorkflowStatus.PLANNING
    assert history[1].destination is WorkflowStatus.EXECUTING

    assert history[2].source is WorkflowStatus.EXECUTING
    assert history[2].destination is WorkflowStatus.COMPLETED


def test_invalid_transition_is_rejected() -> None:
    machine = make_machine()

    with pytest.raises(
        InvalidWorkflowTransition,
        match="Cannot transition workflow",
    ):
        machine.transition_to(WorkflowStatus.COMPLETED)

    assert machine.status is WorkflowStatus.CREATED
    assert machine.history == ()


def test_completed_state_is_terminal() -> None:
    machine = make_machine()

    machine.transition_to(WorkflowStatus.PLANNING)
    machine.transition_to(WorkflowStatus.EXECUTING)
    machine.complete("done")

    with pytest.raises(InvalidWorkflowTransition):
        machine.transition_to(WorkflowStatus.EXECUTING)

    assert machine.status is WorkflowStatus.COMPLETED


def test_failed_state_is_terminal() -> None:
    machine = make_machine()

    machine.transition_to(WorkflowStatus.PLANNING)
    machine.fail("planning failed")

    with pytest.raises(InvalidWorkflowTransition):
        machine.transition_to(WorkflowStatus.EXECUTING)

    assert machine.status is WorkflowStatus.FAILED


def test_workflow_can_fail_during_planning() -> None:
    machine = make_machine()

    machine.transition_to(WorkflowStatus.PLANNING)
    machine.fail("unable to build plan")

    assert machine.status is WorkflowStatus.FAILED
    assert machine.state.error == "unable to build plan"
    assert machine.state.result is None


def test_workflow_can_fail_during_execution() -> None:
    machine = make_machine()

    machine.transition_to(WorkflowStatus.PLANNING)
    machine.transition_to(WorkflowStatus.EXECUTING)
    machine.fail("execution failed")

    assert machine.status is WorkflowStatus.FAILED
    assert machine.state.error == "execution failed"


def test_complete_requires_executing_state() -> None:
    machine = make_machine()

    machine.transition_to(WorkflowStatus.PLANNING)

    with pytest.raises(
        InvalidWorkflowTransition,
        match="only be completed while executing",
    ):
        machine.complete("done")

    assert machine.status is WorkflowStatus.PLANNING


def test_fail_requires_active_workflow() -> None:
    machine = make_machine()

    with pytest.raises(
        InvalidWorkflowTransition,
        match="only fail while planning or executing",
    ):
        machine.fail("error")

    assert machine.status is WorkflowStatus.CREATED


def test_state_preserves_workflow_input() -> None:
    machine = make_machine()

    assert machine.state.input == {
        "task": "test workflow",
    }


def test_history_exposure_does_not_allow_append() -> None:
    machine = make_machine()

    machine.transition_to(WorkflowStatus.PLANNING)

    history = machine.history

    assert isinstance(history, tuple)