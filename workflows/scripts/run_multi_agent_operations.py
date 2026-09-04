from pathlib import Path

from workflows.approval.manager import (
    ApprovalManager,
)
from workflows.contracts.state import (
    WorkflowState,
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
from workflows.resilience.policy import (
    RetryPolicy,
)
from workflows.tracing.recorder import (
    WorkflowTraceRecorder,
)

DATABASE_PATH = Path(
    "data/"
    "sprint06_multi_agent_operations.db"
)


def build_registry() -> WorkerRegistry:
    registry = WorkerRegistry()

    registry.register(
        AccountWorker()
    )

    registry.register(
        TransactionWorker(
            transient_failures=1
        )
    )

    registry.register(
        KnowledgeWorker()
    )

    registry.register(
        FallbackWorker()
    )

    return registry


def build_engine(
    store: SQLiteCheckpointStore,
) -> MultiAgentOperationsEngine:
    return MultiAgentOperationsEngine(
        checkpoint_store=store,
        coordinator=(
            OperationsCoordinator()
        ),
        worker_registry=(
            build_registry()
        ),
        approval_manager=(
            ApprovalManager(store)
        ),
        trace_recorder=(
            WorkflowTraceRecorder()
        ),
        retry_policy=(
            RetryPolicy(
                max_attempts=3,
                delay_seconds=0,
            )
        ),
        sleeper=lambda _: None,
    )


def main() -> None:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    store = SQLiteCheckpointStore(
        DATABASE_PATH
    )

    engine = build_engine(
        store
    )

    state = WorkflowState.create(
        {
            "request": (
                "Transfer money and "
                "explain the policy"
            ),
        },
        workflow_id=(
            "workflow-sprint06-demo-001"
        ),
    )

    print("Starting workflow")
    print()

    suspended = engine.start(
        state
    )

    print(
        f"Status after start: "
        f"{suspended.status.value}"
    )

    approval = ApprovalManager(
        store
    ).get(
        state.workflow_id
    )

    if approval is not None:
        print(
            f"Approval: "
            f"{approval.status.value}"
        )

    print()
    print(
        "Simulating process restart "
        "and human approval..."
    )

    ApprovalManager(
        store
    ).approve(
        state.workflow_id
    )

    new_store = SQLiteCheckpointStore(
        DATABASE_PATH
    )

    new_engine = build_engine(
        new_store
    )

    result = new_engine.resume(
        state.workflow_id
    )

    print()
    print(
        f"Final status: "
        f"{result.status.value}"
    )

    print(
        f"Result: {result.result}"
    )

    print()
    print("Operational trace")

    for index, event in enumerate(
        new_engine.trace,
        start=1,
    ):
        print(
            
                f"{index}. "
                f"type="
                f"{event.event_type.value}, "
                f"node={event.node}, "
                f"worker="
                f"{event.worker_name}, "
                f"attempt="
                f"{event.attempt}"
            
        )


if __name__ == "__main__":
    main()