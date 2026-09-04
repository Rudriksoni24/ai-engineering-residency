from pathlib import Path

import pytest

from workflows.contracts.state import (
    WorkflowState,
    WorkflowStatus,
)
from workflows.core.state_machine import (
    WorkflowStateMachine,
)
from workflows.graph.engine import (
    END,
    WorkflowGraph,
)
from workflows.persistence.contracts import (
    WorkflowCheckpoint,
)
from workflows.persistence.engine import (
    PersistentWorkflowEngine,
    WorkflowCheckpointNotFoundError,
)
from workflows.persistence.sqlite_store import (
    SQLiteCheckpointStore,
)


def classify(
    state: WorkflowState,
) -> WorkflowState:
    task = str(
        state.input.get("task", "")
    )

    state.context["task_type"] = task

    return state


def route_task(
    state: WorkflowState,
) -> str:
    return str(
        state.context["task_type"]
    )


def account_worker(
    state: WorkflowState,
) -> WorkflowState:
    state.result = {
        "handled_by": "account_worker"
    }

    return state


def transaction_worker(
    state: WorkflowState,
) -> WorkflowState:
    state.result = {
        "handled_by": "transaction_worker"
    }

    return state


def build_graph() -> WorkflowGraph:
    graph = WorkflowGraph()

    graph.add_node(
        "classify",
        classify,
    )

    graph.add_node(
        "account_worker",
        account_worker,
    )

    graph.add_node(
        "transaction_worker",
        transaction_worker,
    )

    graph.set_start("classify")

    graph.add_conditional_edges(
        "classify",
        route_task,
        {
            "account": "account_worker",
            "transaction": "transaction_worker",
        },
    )

    graph.add_edge(
        "account_worker",
        END,
    )

    graph.add_edge(
        "transaction_worker",
        END,
    )

    return graph


def make_store(
    tmp_path: Path,
) -> SQLiteCheckpointStore:
    return SQLiteCheckpointStore(
        tmp_path / "workflows.db"
    )


def make_state(
    workflow_id: str,
    task: str = "account",
) -> WorkflowState:
    return WorkflowState.create(
        {
            "task": task,
        },
        workflow_id=workflow_id,
    )


def test_checkpoint_can_be_saved_and_loaded(
    tmp_path: Path,
) -> None:
    store = make_store(tmp_path)

    state = make_state(
        "workflow-001"
    )

    state.context["value"] = 42

    checkpoint = WorkflowCheckpoint(
        workflow_id=state.workflow_id,
        state=state,
        next_node="account_worker",
        completed=False,
    )

    store.save(checkpoint)

    loaded = store.load(
        "workflow-001"
    )

    assert loaded is not None
    assert loaded.workflow_id == "workflow-001"
    assert loaded.next_node == "account_worker"
    assert loaded.completed is False
    assert loaded.state.context == {
        "value": 42,
    }


def test_state_survives_new_store_instance(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "workflows.db"
    )

    first_store = SQLiteCheckpointStore(
        database_path
    )

    state = make_state(
        "workflow-001"
    )

    state.context["persisted"] = True

    first_store.save(
        WorkflowCheckpoint(
            workflow_id=state.workflow_id,
            state=state,
            next_node="account_worker",
        )
    )

    second_store = SQLiteCheckpointStore(
        database_path
    )

    loaded = second_store.load(
        "workflow-001"
    )

    assert loaded is not None

    assert loaded.state.context == {
        "persisted": True,
    }


def test_workflow_resumes_from_saved_node(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "workflows.db"
    )

    graph = build_graph()

    first_store = SQLiteCheckpointStore(
        database_path
    )

    first_engine = PersistentWorkflowEngine(
        graph,
        first_store,
    )

    state = make_state(
        "workflow-001",
        task="account",
    )

    first_engine.start(
        state,
        stop_after_steps=1,
    )

    checkpoint = first_store.load(
        "workflow-001"
    )

    assert checkpoint is not None

    assert (
        checkpoint.next_node
        == "account_worker"
    )

    assert checkpoint.state.context == {
        "task_type": "account",
    }

    second_store = SQLiteCheckpointStore(
        database_path
    )

    second_engine = PersistentWorkflowEngine(
        graph,
        second_store,
    )

    final_state = second_engine.resume(
        "workflow-001"
    )

    assert final_state.result == {
        "handled_by": "account_worker",
    }


def test_resume_does_not_repeat_completed_node(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "workflows.db"
    )

    calls = {
        "classify": 0,
        "worker": 0,
    }

    def counted_classify(
        state: WorkflowState,
    ) -> WorkflowState:
        calls["classify"] += 1
        state.context["route"] = "worker"
        return state

    def router(
        state: WorkflowState,
    ) -> str:
        return str(
            state.context["route"]
        )

    def counted_worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls["worker"] += 1
        state.result = "done"
        return state

    graph = WorkflowGraph()

    graph.add_node(
        "classify",
        counted_classify,
    )

    graph.add_node(
        "worker",
        counted_worker,
    )

    graph.set_start("classify")

    graph.add_conditional_edges(
        "classify",
        router,
        {
            "worker": "worker",
        },
    )

    graph.add_edge(
        "worker",
        END,
    )

    first_engine = PersistentWorkflowEngine(
        graph,
        SQLiteCheckpointStore(
            database_path
        ),
    )

    state = make_state(
        "workflow-001"
    )

    first_engine.start(
        state,
        stop_after_steps=1,
    )

    assert calls["classify"] == 1
    assert calls["worker"] == 0

    second_engine = PersistentWorkflowEngine(
        graph,
        SQLiteCheckpointStore(
            database_path
        ),
    )

    second_engine.resume(
        "workflow-001"
    )

    assert calls["classify"] == 1
    assert calls["worker"] == 1


def test_checkpoints_are_isolated_by_workflow_id(
    tmp_path: Path,
) -> None:
    store = make_store(tmp_path)

    first = make_state(
        "workflow-001",
        "account",
    )

    second = make_state(
        "workflow-002",
        "transaction",
    )

    store.save(
        WorkflowCheckpoint(
            workflow_id=first.workflow_id,
            state=first,
            next_node="account_worker",
        )
    )

    store.save(
        WorkflowCheckpoint(
            workflow_id=second.workflow_id,
            state=second,
            next_node="transaction_worker",
        )
    )

    first_loaded = store.load(
        "workflow-001"
    )

    second_loaded = store.load(
        "workflow-002"
    )

    assert first_loaded is not None
    assert second_loaded is not None

    assert (
        first_loaded.next_node
        == "account_worker"
    )

    assert (
        second_loaded.next_node
        == "transaction_worker"
    )


def test_completed_workflow_can_be_loaded(
    tmp_path: Path,
) -> None:
    store = make_store(tmp_path)

    engine = PersistentWorkflowEngine(
        build_graph(),
        store,
    )

    state = make_state(
        "workflow-001",
        "transaction",
    )

    final_state = engine.start(
        state
    )

    assert final_state.result == {
        "handled_by": "transaction_worker",
    }

    checkpoint = store.load(
        "workflow-001"
    )

    assert checkpoint is not None
    assert checkpoint.completed is True
    assert checkpoint.next_node == END


def test_resuming_completed_workflow_does_not_execute_again(
    tmp_path: Path,
) -> None:
    calls = {
        "worker": 0,
    }

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls["worker"] += 1
        state.result = "done"
        return state

    graph = WorkflowGraph()

    graph.add_node(
        "worker",
        worker,
    )

    graph.set_start("worker")

    graph.add_edge(
        "worker",
        END,
    )

    store = make_store(tmp_path)

    engine = PersistentWorkflowEngine(
        graph,
        store,
    )

    state = make_state(
        "workflow-001"
    )

    engine.start(state)

    assert calls["worker"] == 1

    result = engine.resume(
        "workflow-001"
    )

    assert calls["worker"] == 1
    assert result.result == "done"


def test_missing_checkpoint_returns_none(
    tmp_path: Path,
) -> None:
    store = make_store(tmp_path)

    assert (
        store.load("missing-workflow")
        is None
    )


def test_resume_missing_workflow_fails_safely(
    tmp_path: Path,
) -> None:
    engine = PersistentWorkflowEngine(
        build_graph(),
        make_store(tmp_path),
    )

    with pytest.raises(
        WorkflowCheckpointNotFoundError,
        match="No checkpoint found",
    ):
        engine.resume(
            "missing-workflow"
        )

def test_transition_history_survives_persistence(
    tmp_path: Path,
) -> None:
    store = make_store(tmp_path)

    state = make_state(
        "workflow-history"
    )

    machine = WorkflowStateMachine(
        state
    )

    machine.transition_to(
        WorkflowStatus.PLANNING
    )

    machine.transition_to(
        WorkflowStatus.EXECUTING
    )

    store.save(
        WorkflowCheckpoint(
            workflow_id=state.workflow_id,
            state=state,
            next_node="account_worker",
        )
    )

    loaded = store.load(
        "workflow-history"
    )

    assert loaded is not None

    assert len(
        loaded.state.history
    ) == 2

    assert (
        loaded.state.history[0].source
        is WorkflowStatus.CREATED
    )

    assert (
        loaded.state.history[0].destination
        is WorkflowStatus.PLANNING
    )