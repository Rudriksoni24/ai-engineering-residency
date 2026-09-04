from pathlib import Path

from workflows.contracts.state import WorkflowState
from workflows.graph.engine import END, WorkflowGraph
from workflows.persistence.engine import (
    PersistentWorkflowEngine,
)
from workflows.persistence.sqlite_store import (
    SQLiteCheckpointStore,
)

DATABASE_PATH = Path(
    "data/sprint06_workflows.db"
)


def classify_request(
    state: WorkflowState,
) -> WorkflowState:
    request = str(
        state.input.get("request", "")
    ).lower()

    if "account" in request:
        state.context["task_type"] = "account"

    elif "transaction" in request:
        state.context["task_type"] = "transaction"

    else:
        state.context["task_type"] = "unsupported"

    return state


def route_request(
    state: WorkflowState,
) -> str:
    return str(
        state.context.get(
            "task_type",
            "unsupported",
        )
    )


def account_worker(
    state: WorkflowState,
) -> WorkflowState:
    state.result = {
        "worker": "account_worker",
        "message": "Handled account request.",
    }

    return state


def transaction_worker(
    state: WorkflowState,
) -> WorkflowState:
    state.result = {
        "worker": "transaction_worker",
        "message": "Handled transaction request.",
    }

    return state


def fallback(
    state: WorkflowState,
) -> WorkflowState:
    state.result = {
        "worker": "fallback",
        "message": "Unsupported request.",
    }

    return state


def build_graph() -> WorkflowGraph:
    graph = WorkflowGraph()

    graph.add_node(
        "classify",
        classify_request,
    )

    graph.add_node(
        "account_worker",
        account_worker,
    )

    graph.add_node(
        "transaction_worker",
        transaction_worker,
    )

    graph.add_node(
        "fallback",
        fallback,
    )

    graph.set_start("classify")

    graph.add_conditional_edges(
        "classify",
        route_request,
        {
            "account": "account_worker",
            "transaction": "transaction_worker",
            "unsupported": "fallback",
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

    graph.add_edge(
        "fallback",
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

    first_engine = PersistentWorkflowEngine(
        graph,
        store,
    )

    state = WorkflowState.create(
        {
            "request": "Show account ACC001",
        },
        workflow_id="workflow-persistent-demo-001",
    )

    print("Starting workflow")

    interrupted_state = first_engine.start(
        state,
        stop_after_steps=1,
    )

    print(
        "State after simulated interruption:"
    )
    print(interrupted_state.context)

    checkpoint = store.load(
        state.workflow_id
    )

    if checkpoint is None:
        raise RuntimeError(
            "Expected checkpoint to exist."
        )

    print(
        f"Saved next node: "
        f"{checkpoint.next_node}"
    )

    print()
    print(
        "Creating new engine instance..."
    )

    new_store = SQLiteCheckpointStore(
        DATABASE_PATH
    )

    second_engine = PersistentWorkflowEngine(
        graph,
        new_store,
    )

    final_state = second_engine.resume(
        state.workflow_id
    )

    print()
    print("Workflow resumed")
    print(f"Result: {final_state.result}")

    completed_checkpoint = (
        second_engine.load(
            state.workflow_id
        )
    )

    if completed_checkpoint is not None:
        print(
            "Completed: "
            f"{completed_checkpoint.completed}"
        )


if __name__ == "__main__":
    main()

    # uv run python -m workflows.scripts.run_persistent_workflow