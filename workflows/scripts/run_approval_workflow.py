from pathlib import Path

from workflows.approval.contracts import (
    WorkflowApprovalPendingError,
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

DATABASE_PATH = Path(
    "data/sprint06_approval.db"
)


def prepare_transfer(
    state: WorkflowState,
) -> WorkflowState:
    state.context["transfer"] = {
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 250000,
    }

    return state


def transfer_worker(
    state: WorkflowState,
) -> WorkflowState:
    transfer = state.context[
        "transfer"
    ]

    state.result = {
        "status": "transferred",
        "from_account": (
            transfer["from_account"]
        ),
        "to_account": (
            transfer["to_account"]
        ),
        "amount": transfer["amount"],
    }

    return state


def build_graph() -> WorkflowGraph:
    graph = WorkflowGraph()

    graph.add_node(
        "prepare_transfer",
        prepare_transfer,
    )

    graph.add_node(
        "transfer_worker",
        transfer_worker,
    )

    graph.set_start(
        "prepare_transfer"
    )

    graph.add_edge(
        "prepare_transfer",
        "transfer_worker",
    )

    graph.add_edge(
        "transfer_worker",
        END,
    )

    return graph


def main() -> None:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    store = SQLiteCheckpointStore(
        DATABASE_PATH
    )

    graph = build_graph()

    persistent_engine = (
        PersistentWorkflowEngine(
            graph,
            store,
        )
    )

    approval_manager = (
        ApprovalManager(store)
    )

    approval_engine = (
        ApprovalWorkflowEngine(
            persistent_engine,
            approval_manager,
        )
    )

    state = WorkflowState.create(
        {
            "request": (
                "Transfer 250000 from "
                "ACC001 to ACC002"
            ),
        },
        workflow_id=(
            "workflow-approval-demo-001"
        ),
    )

    print("Preparing transfer...")

    persistent_engine.start(
        state,
        stop_after_steps=1,
    )

    checkpoint = store.load(
        state.workflow_id
    )

    if checkpoint is None:
        raise RuntimeError(
            "Expected checkpoint."
        )

    approval = (
        approval_manager
        .request_approval(
            checkpoint.state,
            next_node=(
                checkpoint.next_node
            ),
            action="transfer_money",
            reason=(
                "Transfer amount requires "
                "human approval."
            ),
            metadata={
                "amount": 250000,
                "from_account": "ACC001",
                "to_account": "ACC002",
            },
            approval_id=(
                "approval-demo-001"
            ),
        )
    )

    print()
    print(
        f"Approval status: "
        f"{approval.status.value}"
    )

    print(
        f"Protected next node: "
        f"{checkpoint.next_node}"
    )

    print()
    print(
        "Attempting resume before "
        "approval..."
    )

    try:
        approval_engine.resume(
            state.workflow_id
        )
    except WorkflowApprovalPendingError:
        print(
            "Workflow correctly suspended."
        )

    print()
    print(
        "Simulating external human "
        "approval..."
    )

    approved = (
        approval_manager.approve(
            state.workflow_id
        )
    )

    print(
        f"Approval status: "
        f"{approved.status.value}"
    )

    print()
    print(
        "Creating fresh runtime "
        "instances..."
    )

    new_store = SQLiteCheckpointStore(
        DATABASE_PATH
    )

    new_persistent_engine = (
        PersistentWorkflowEngine(
            graph,
            new_store,
        )
    )

    new_approval_manager = (
        ApprovalManager(new_store)
    )

    new_approval_engine = (
        ApprovalWorkflowEngine(
            new_persistent_engine,
            new_approval_manager,
        )
    )

    final_state = (
        new_approval_engine.resume(
            state.workflow_id
        )
    )

    print()
    print(
        f"Result: {final_state.result}"
    )


if __name__ == "__main__":
    main()