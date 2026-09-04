from pathlib import Path

import pytest

from workflows.approval.contracts import (
    ApprovalStatus,
    WorkflowApprovalPendingError,
    WorkflowApprovalRejectedError,
)
from workflows.approval.manager import (
    ApprovalManager,
)
from workflows.contracts.state import (
    WorkflowState,
    WorkflowStatus,
)
from workflows.coordination.registry import (
    WorkerRegistry,
)
from workflows.operations.coordinator import (
    OperationsCoordinator,
)
from workflows.operations.engine import (
    MultiAgentOperationsEngine,
)
from workflows.operations.workers import (
    AccountWorker,
    FallbackWorker,
    KnowledgeWorker,
    TransactionWorker,
)
from workflows.persistence.sqlite_store import (
    SQLiteCheckpointStore,
)
from workflows.resilience.contracts import (
    RecoverableWorkflowError,
    RetryExhaustedError,
)
from workflows.resilience.policy import (
    RetryPolicy,
)
from workflows.tracing.contracts import (
    WorkflowEventType,
)
from workflows.tracing.recorder import (
    WorkflowTraceRecorder,
)


def make_store(
    tmp_path: Path,
) -> SQLiteCheckpointStore:
    return SQLiteCheckpointStore(
        tmp_path / "workflow.db"
    )


def make_registry(
    *,
    transaction_failures: int = 0,
) -> WorkerRegistry:
    registry = WorkerRegistry()

    registry.register(
        AccountWorker()
    )

    registry.register(
        TransactionWorker(
            transient_failures=(
                transaction_failures
            )
        )
    )

    registry.register(
        KnowledgeWorker()
    )

    registry.register(
        FallbackWorker()
    )

    return registry


def make_engine(
    tmp_path: Path,
    *,
    transaction_failures: int = 0,
    max_attempts: int = 3,
) -> tuple[
    MultiAgentOperationsEngine,
    SQLiteCheckpointStore,
]:
    store = make_store(
        tmp_path
    )

    approval_manager = (
        ApprovalManager(store)
    )

    engine = (
        MultiAgentOperationsEngine(
            checkpoint_store=store,
            coordinator=(
                OperationsCoordinator()
            ),
            worker_registry=(
                make_registry(
                    transaction_failures=(
                        transaction_failures
                    )
                )
            ),
            approval_manager=(
                approval_manager
            ),
            trace_recorder=(
                WorkflowTraceRecorder()
            ),
            retry_policy=(
                RetryPolicy(
                    max_attempts=(
                        max_attempts
                    ),
                    delay_seconds=0,
                )
            ),
            sleeper=lambda _: None,
        )
    )

    return engine, store


def make_state(
    request: str,
    *,
    workflow_id: str = "workflow-001",
) -> WorkflowState:
    return WorkflowState.create(
        {
            "request": request,
        },
        workflow_id=workflow_id,
    )


def event_types(
    engine: MultiAgentOperationsEngine,
) -> list[WorkflowEventType]:
    return [
        event.event_type
        for event in engine.trace
    ]


def test_account_workflow_completes(
    tmp_path: Path,
) -> None:
    engine, store = make_engine(
        tmp_path
    )

    state = make_state(
        "Show account ACC001"
    )

    result = engine.start(state)

    assert (
        result.status
        is WorkflowStatus.COMPLETED
    )

    assert result.result == [
        {
            "worker_name": "account",
            "output": {
                "account_id": "ACC001",
                "status": "active",
            },
        }
    ]

    checkpoint = store.load(
        state.workflow_id
    )

    assert checkpoint is not None
    assert checkpoint.completed is True


def test_account_workflow_does_not_require_approval(
    tmp_path: Path,
) -> None:
    engine, store = make_engine(
        tmp_path
    )

    state = make_state(
        "Show account ACC001"
    )

    engine.start(state)

    manager = ApprovalManager(
        store
    )

    assert (
        manager.get(
            state.workflow_id
        )
        is None
    )


def test_transaction_workflow_suspends_for_approval(
    tmp_path: Path,
) -> None:
    engine, store = make_engine(
        tmp_path
    )

    state = make_state(
        (
            "Transfer money using "
            "transaction TXN9001"
        )
    )

    result = engine.start(state)

    assert (
        result.status
        is WorkflowStatus.EXECUTING
    )

    approval = ApprovalManager(
        store
    ).get(
        state.workflow_id
    )

    assert approval is not None

    assert (
        approval.status
        is ApprovalStatus.PENDING
    )

    assert (
        "worker_results"
        not in result.context
    )


def test_pending_transaction_cannot_resume(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path
    )

    state = make_state(
        "Transfer money"
    )

    engine.start(state)

    with pytest.raises(
        WorkflowApprovalPendingError
    ):
        engine.resume(
            state.workflow_id
        )


def test_approved_transaction_resumes_and_completes(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path
    )

    state = make_state(
        "Transfer money"
    )

    engine.start(state)

    engine.approve(
        state.workflow_id
    )

    result = engine.resume(
        state.workflow_id
    )

    assert (
        result.status
        is WorkflowStatus.COMPLETED
    )

    assert result.result == [
        {
            "worker_name": (
                "transaction"
            ),
            "output": {
                "transaction_id": (
                    "TXN9001"
                ),
                "status": "completed",
            },
        }
    ]


def test_rejected_transaction_remains_blocked(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path
    )

    state = make_state(
        "Transfer money"
    )

    engine.start(state)

    engine.reject(
        state.workflow_id
    )

    with pytest.raises(
        WorkflowApprovalRejectedError
    ):
        engine.resume(
            state.workflow_id
        )


def test_multi_worker_request_executes_all_workers(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path
    )

    state = make_state(
        (
            "Show account ACC001 "
            "and explain the policy"
        )
    )

    result = engine.start(state)

    names = [
        item["worker_name"]
        for item in result.result
    ]

    assert names == [
        "account",
        "knowledge",
    ]


def test_transaction_worker_recovers_after_transient_failure(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path,
        transaction_failures=1,
        max_attempts=3,
    )

    state = make_state(
        "Transfer money"
    )

    engine.start(state)

    engine.approve(
        state.workflow_id
    )

    result = engine.resume(
        state.workflow_id
    )

    assert (
        result.status
        is WorkflowStatus.COMPLETED
    )

    types = event_types(engine)

    assert (
        WorkflowEventType
        .ATTEMPT_FAILED
        in types
    )

    assert (
        WorkflowEventType
        .RETRY_SCHEDULED
        in types
    )

    assert (
        WorkflowEventType
        .WORKER_COMPLETED
        in types
    )


def test_retry_exhaustion_fails_workflow(
    tmp_path: Path,
) -> None:
    engine, store = make_engine(
        tmp_path,
        transaction_failures=5,
        max_attempts=2,
    )

    state = make_state(
        "Transfer money"
    )

    engine.start(state)

    engine.approve(
        state.workflow_id
    )

    with pytest.raises(
        RetryExhaustedError
    ):
        engine.resume(
            state.workflow_id
        )

    checkpoint = store.load(
        state.workflow_id
    )

    assert checkpoint is not None

    assert (
        checkpoint.state.status
        is WorkflowStatus.FAILED
    )


def test_fallback_worker_handles_unknown_request(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path
    )

    result = engine.start(
        make_state(
            "Tell me something random"
        )
    )

    assert result.result == [
        {
            "worker_name": "fallback",
            "output": {
                "message": (
                    "No specialized worker "
                    "matched the request."
                ),
            },
        }
    ]


def test_trace_contains_full_success_lifecycle(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path
    )

    engine.start(
        make_state(
            "Show account ACC001"
        )
    )

    types = event_types(engine)

    assert (
        WorkflowEventType
        .WORKFLOW_STARTED
        in types
    )

    assert (
        WorkflowEventType
        .LIFECYCLE_TRANSITION
        in types
    )

    assert (
        WorkflowEventType
        .NODE_STARTED
        in types
    )

    assert (
        WorkflowEventType
        .WORKER_DELEGATED
        in types
    )

    assert (
        WorkflowEventType
        .WORKER_COMPLETED
        in types
    )

    assert (
        WorkflowEventType
        .CHECKPOINT_SAVED
        in types
    )

    assert (
        WorkflowEventType
        .WORKFLOW_COMPLETED
        in types
    )


def test_trace_records_approval_suspension(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path
    )

    engine.start(
        make_state(
            "Transfer money"
        )
    )

    types = event_types(engine)

    assert (
        WorkflowEventType
        .APPROVAL_REQUESTED
        in types
    )

    assert (
        WorkflowEventType
        .WORKFLOW_SUSPENDED
        in types
    )


def test_checkpoint_survives_new_runtime(
    tmp_path: Path,
) -> None:
    database_path = (
        tmp_path / "workflow.db"
    )

    first_store = (
        SQLiteCheckpointStore(
            database_path
        )
    )

    first_manager = ApprovalManager(
        first_store
    )

    first_engine = (
        MultiAgentOperationsEngine(
            checkpoint_store=(
                first_store
            ),
            coordinator=(
                OperationsCoordinator()
            ),
            worker_registry=(
                make_registry()
            ),
            approval_manager=(
                first_manager
            ),
            trace_recorder=(
                WorkflowTraceRecorder()
            ),
            retry_policy=(
                RetryPolicy(
                    max_attempts=3
                )
            ),
            sleeper=lambda _: None,
        )
    )

    state = make_state(
        "Transfer money"
    )

    first_engine.start(state)

    first_manager.approve(
        state.workflow_id
    )

    second_store = (
        SQLiteCheckpointStore(
            database_path
        )
    )

    second_manager = ApprovalManager(
        second_store
    )

    second_engine = (
        MultiAgentOperationsEngine(
            checkpoint_store=(
                second_store
            ),
            coordinator=(
                OperationsCoordinator()
            ),
            worker_registry=(
                make_registry()
            ),
            approval_manager=(
                second_manager
            ),
            trace_recorder=(
                WorkflowTraceRecorder()
            ),
            retry_policy=(
                RetryPolicy(
                    max_attempts=3
                )
            ),
            sleeper=lambda _: None,
        )
    )

    result = second_engine.resume(
        state.workflow_id
    )

    assert (
        result.status
        is WorkflowStatus.COMPLETED
    )


def test_completed_workflow_loads_without_rerunning(
    tmp_path: Path,
) -> None:
    engine, _ = make_engine(
        tmp_path
    )

    state = make_state(
        "Show account ACC001"
    )

    first = engine.start(state)

    second = engine.resume(
        state.workflow_id
    )

    assert second.result == first.result
    assert (
        second.status
        is WorkflowStatus.COMPLETED
    )

def test_terminal_worker_failure_is_not_retried(
    tmp_path: Path,
) -> None:
    class TerminalWorker:
        def __init__(self) -> None:
            self.calls = 0

        @property
        def name(self) -> str:
            return "account"

        def run(
            self,
            task: str,
            state: WorkflowState,
        ):
            self.calls += 1

            raise ValueError(
                "invalid account"
            )

    worker = TerminalWorker()

    store = make_store(
        tmp_path
    )

    registry = WorkerRegistry()
    registry.register(worker)
    registry.register(
        FallbackWorker()
    )

    engine = (
        MultiAgentOperationsEngine(
            checkpoint_store=store,
            coordinator=(
                OperationsCoordinator()
            ),
            worker_registry=registry,
            approval_manager=(
                ApprovalManager(store)
            ),
            trace_recorder=(
                WorkflowTraceRecorder()
            ),
            retry_policy=(
                RetryPolicy(
                    max_attempts=5
                )
            ),
            sleeper=lambda _: None,
        )
    )

    with pytest.raises(
        ValueError,
        match="invalid account",
    ):
        engine.start(
            make_state(
                "Show account ACC001"
            )
        )

    assert worker.calls == 1