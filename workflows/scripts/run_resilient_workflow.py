from pathlib import Path

from workflows.contracts.state import (
    WorkflowState,
)
from workflows.graph.engine import (
    END,
    WorkflowGraph,
)
from workflows.persistence.sqlite_store import (
    SQLiteCheckpointStore,
)
from workflows.resilience.contracts import (
    RecoverableWorkflowError,
)
from workflows.resilience.engine import (
    ResilientWorkflowEngine,
)
from workflows.resilience.policy import (
    RetryPolicy,
)

DATABASE_PATH = Path(
    "data/sprint06_resilience.db"
)


class FlakyTransactionWorker:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(
        self,
        state: WorkflowState,
    ) -> WorkflowState:
        self.calls += 1

        print(
            f"Transaction attempt "
            f"{self.calls}"
        )

        if self.calls < 3:
            raise (
                RecoverableWorkflowError(
                    "Temporary banking "
                    "service outage."
                )
            )

        state.result = {
            "transaction_id": "TXN9001",
            "status": "completed",
            "attempts": self.calls,
        }

        return state


def build_graph(
    worker: FlakyTransactionWorker,
) -> WorkflowGraph:
    graph = WorkflowGraph()

    graph.add_node(
        "transaction_worker",
        worker,
    )

    graph.set_start(
        "transaction_worker"
    )

    graph.add_edge(
        "transaction_worker",
        END,
    )

    return graph


def main() -> None:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    worker = (
        FlakyTransactionWorker()
    )

    graph = build_graph(worker)

    store = SQLiteCheckpointStore(
        DATABASE_PATH
    )

    engine = ResilientWorkflowEngine(
        graph,
        store,
        retry_policy=RetryPolicy(
            max_attempts=3,
            delay_seconds=0.0,
        ),
    )

    state = WorkflowState.create(
        {
            "request": (
                "Process transaction "
                "TXN9001"
            ),
        },
        workflow_id=(
            "workflow-resilience-demo-001"
        ),
    )

    result = engine.start(state)

    print()
    print(
        f"Result: {result.result}"
    )

    print()
    print("Retry trace")

    for event in engine.trace:
        print(
            
                f"type="
                f"{event.event_type.value}, "
                f"node={event.node}, "
                f"attempt={event.attempt}, "
                f"error="
                f"{event.error_message}"
            
        )


if __name__ == "__main__":
    main()