from pathlib import Path

import pytest

from workflows.approval.contracts import (
    ApprovalAlreadyDecidedError,
    ApprovalNotFoundError,
    ApprovalStatus,
    WorkflowApprovalPendingError,
    WorkflowApprovalRejectedError,
)
from workflows.approval.engine import (
    ApprovalWorkflowEngine,
)
from workflows.approval.manager import (
    ApprovalManager,
)
from workflows.contracts.state import (
    WorkflowState,
)
from workflows.graph.engine import (
    END,
    WorkflowGraph,
)
from workflows.persistence.engine import (
    PersistentWorkflowEngine,
)
from workflows.persistence.sqlite_store import (
    SQLiteCheckpointStore,
)


def build_graph(
    worker_calls: list[str] | None = None,
) -> WorkflowGraph:
    calls = (
        worker_calls
        if worker_calls is not None
        else []
    )

    def prepare(
        state: WorkflowState,
    ) -> WorkflowState:
        state.context[
            "prepared"
        ] = True

        return state

    def protected_worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(
            "protected_worker"
        )

        state.result = "executed"

        return state

    graph = WorkflowGraph()

    graph.add_node(
        "prepare",
        prepare,
    )

    graph.add_node(
        "protected_worker",
        protected_worker,
    )

    graph.set_start("prepare")

    graph.add_edge(
        "prepare",
        "protected_worker",
    )

    graph.add_edge(
        "protected_worker",
        END,
    )

    return graph


def make_store(
    tmp_path: Path,
) -> SQLiteCheckpointStore:
    return SQLiteCheckpointStore(
        tmp_path / "workflow.db"
    )


def prepare_pending_workflow(
    tmp_path: Path,
    *,
    worker_calls: list[str] | None = None,
) -> tuple[
    SQLiteCheckpointStore,
    ApprovalManager,
    ApprovalWorkflowEngine,
    WorkflowState,
]:
    store = make_store(tmp_path)

    graph = build_graph(
        worker_calls
    )

    persistent_engine = (
        PersistentWorkflowEngine(
            graph,
            store,
        )
    )

    manager = ApprovalManager(
        store
    )

    approval_engine = (
        ApprovalWorkflowEngine(
            persistent_engine,
            manager,
        )
    )

    state = WorkflowState.create(
        {
            "request": "sensitive action",
        },
        workflow_id="workflow-001",
    )

    persistent_engine.start(
        state,
        stop_after_steps=1,
    )

    checkpoint = store.load(
        state.workflow_id
    )

    assert checkpoint is not None

    manager.request_approval(
        checkpoint.state,
        next_node=(
            checkpoint.next_node
        ),
        action="protected_action",
        reason="Human approval required.",
        metadata={
            "amount": 1000,
        },
        approval_id="approval-001",
    )

    return (
        store,
        manager,
        approval_engine,
        state,
    )


def test_request_approval_creates_pending_state(
    tmp_path: Path,
) -> None:
    (
        _,
        manager,
        _,
        state,
    ) = prepare_pending_workflow(
        tmp_path
    )

    approval = manager.get(
        state.workflow_id
    )

    assert approval is not None

    assert (
        approval.status
        is ApprovalStatus.PENDING
    )

    assert (
        approval.approval_id
        == "approval-001"
    )

    assert (
        approval.action
        == "protected_action"
    )


def test_approval_metadata_is_persisted(
    tmp_path: Path,
) -> None:
    (
        _,
        manager,
        _,
        state,
    ) = prepare_pending_workflow(
        tmp_path
    )

    approval = manager.get(
        state.workflow_id
    )

    assert approval is not None

    assert approval.metadata == {
        "amount": 1000,
    }


def test_pending_workflow_cannot_resume(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        engine,
        state,
    ) = prepare_pending_workflow(
        tmp_path
    )

    with pytest.raises(
        WorkflowApprovalPendingError,
        match="waiting for approval",
    ):
        engine.resume(
            state.workflow_id
        )


def test_pending_workflow_does_not_execute_protected_worker(
    tmp_path: Path,
) -> None:
    worker_calls: list[str] = []

    (
        _,
        _,
        engine,
        state,
    ) = prepare_pending_workflow(
        tmp_path,
        worker_calls=worker_calls,
    )

    with pytest.raises(
        WorkflowApprovalPendingError
    ):
        engine.resume(
            state.workflow_id
        )

    assert worker_calls == []


def test_approve_changes_status(
    tmp_path: Path,
) -> None:
    (
        _,
        manager,
        _,
        state,
    ) = prepare_pending_workflow(
        tmp_path
    )

    approval = manager.approve(
        state.workflow_id
    )

    assert (
        approval.status
        is ApprovalStatus.APPROVED
    )


def test_approved_workflow_can_resume(
    tmp_path: Path,
) -> None:
    worker_calls: list[str] = []

    (
        _,
        manager,
        engine,
        state,
    ) = prepare_pending_workflow(
        tmp_path,
        worker_calls=worker_calls,
    )

    manager.approve(
        state.workflow_id
    )

    result = engine.resume(
        state.workflow_id
    )

    assert result.result == "executed"

    assert worker_calls == [
        "protected_worker",
    ]


def test_reject_changes_status(
    tmp_path: Path,
) -> None:
    (
        _,
        manager,
        _,
        state,
    ) = prepare_pending_workflow(
        tmp_path
    )

    approval = manager.reject(
        state.workflow_id
    )

    assert (
        approval.status
        is ApprovalStatus.REJECTED
    )


def test_rejected_workflow_cannot_resume(
    tmp_path: Path,
) -> None:
    worker_calls: list[str] = []

    (
        _,
        manager,
        engine,
        state,
    ) = prepare_pending_workflow(
        tmp_path,
        worker_calls=worker_calls,
    )

    manager.reject(
        state.workflow_id
    )

    with pytest.raises(
        WorkflowApprovalRejectedError,
        match="was rejected",
    ):
        engine.resume(
            state.workflow_id
        )

    assert worker_calls == []


def test_approval_survives_new_manager_instance(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "workflow.db"
    )

    store = SQLiteCheckpointStore(
        database_path
    )

    graph = build_graph()

    persistent_engine = (
        PersistentWorkflowEngine(
            graph,
            store,
        )
    )

    state = WorkflowState.create(
        {
            "request": "sensitive",
        },
        workflow_id="workflow-001",
    )

    persistent_engine.start(
        state,
        stop_after_steps=1,
    )

    checkpoint = store.load(
        state.workflow_id
    )

    assert checkpoint is not None

    first_manager = ApprovalManager(
        store
    )

    first_manager.request_approval(
        checkpoint.state,
        next_node=(
            checkpoint.next_node
        ),
        action="protected_action",
        reason="Approval required.",
        approval_id="approval-001",
    )

    second_store = (
        SQLiteCheckpointStore(
            database_path
        )
    )

    second_manager = ApprovalManager(
        second_store
    )

    loaded = second_manager.get(
        "workflow-001"
    )

    assert loaded is not None

    assert (
        loaded.status
        is ApprovalStatus.PENDING
    )


def test_approved_workflow_resumes_with_new_engine_instance(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "workflow.db"
    )

    calls: list[str] = []

    graph = build_graph(calls)

    first_store = (
        SQLiteCheckpointStore(
            database_path
        )
    )

    first_persistent_engine = (
        PersistentWorkflowEngine(
            graph,
            first_store,
        )
    )

    state = WorkflowState.create(
        {
            "request": "sensitive",
        },
        workflow_id="workflow-001",
    )

    first_persistent_engine.start(
        state,
        stop_after_steps=1,
    )

    checkpoint = first_store.load(
        state.workflow_id
    )

    assert checkpoint is not None

    first_manager = ApprovalManager(
        first_store
    )

    first_manager.request_approval(
        checkpoint.state,
        next_node=(
            checkpoint.next_node
        ),
        action="protected_action",
        reason="Approval required.",
        approval_id="approval-001",
    )

    first_manager.approve(
        state.workflow_id
    )

    second_store = (
        SQLiteCheckpointStore(
            database_path
        )
    )

    second_persistent_engine = (
        PersistentWorkflowEngine(
            graph,
            second_store,
        )
    )

    second_manager = (
        ApprovalManager(
            second_store
        )
    )

    second_engine = (
        ApprovalWorkflowEngine(
            second_persistent_engine,
            second_manager,
        )
    )

    result = second_engine.resume(
        state.workflow_id
    )

    assert result.result == "executed"

    assert calls == [
        "protected_worker",
    ]


def test_approval_cannot_be_decided_twice(
    tmp_path: Path,
) -> None:
    (
        _,
        manager,
        _,
        state,
    ) = prepare_pending_workflow(
        tmp_path
    )

    manager.approve(
        state.workflow_id
    )

    with pytest.raises(
        ApprovalAlreadyDecidedError,
        match="already",
    ):
        manager.reject(
            state.workflow_id
        )


def test_missing_workflow_cannot_be_approved(
    tmp_path: Path,
) -> None:
    manager = ApprovalManager(
        make_store(tmp_path)
    )

    with pytest.raises(
        ApprovalNotFoundError,
        match="No workflow checkpoint",
    ):
        manager.approve(
            "missing-workflow"
        )


def test_workflow_without_approval_uses_normal_resume(
    tmp_path: Path,
) -> None:
    store = make_store(tmp_path)

    graph = build_graph()

    persistent_engine = (
        PersistentWorkflowEngine(
            graph,
            store,
        )
    )

    approval_engine = (
        ApprovalWorkflowEngine(
            persistent_engine,
            ApprovalManager(store),
        )
    )

    state = WorkflowState.create(
        {
            "request": "normal",
        },
        workflow_id="workflow-normal",
    )

    persistent_engine.start(
        state,
        stop_after_steps=1,
    )

    result = approval_engine.resume(
        state.workflow_id
    )

    assert result.result == "executed"

    # uv run python -m workflows.scripts.run_approval_workflow