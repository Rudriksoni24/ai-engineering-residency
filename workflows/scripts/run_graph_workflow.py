from workflows.contracts.state import WorkflowState
from workflows.graph.engine import END, WorkflowGraph, WorkflowGraphEngine


def classify_request(
    state: WorkflowState,
) -> WorkflowState:
    request = str(state.input.get("request", "")).lower()

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
        router=route_request,
        routes={
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
    state = WorkflowState.create(
        {
            "request": "Show details for account ACC001",
        },
        workflow_id="workflow-graph-demo-001",
    )

    graph = build_graph()

    engine = WorkflowGraphEngine(graph)

    final_state = engine.run(state)

    print("Workflow result")
    print(final_state.result)
    print()

    print("Workflow context")
    print(final_state.context)
    print()

    print("Execution trace")

    for index, event in enumerate(
        engine.trace,
        start=1,
    ):
        print(
            f"{index}. "
            f"type={event.event_type.value}, "
            f"node={event.node}, "
            f"source={event.source}, "
            f"destination={event.destination}, "
            f"route={event.route}"
        )


if __name__ == "__main__":
    main()

    #uv run python -m workflows.scripts.run_graph_workflow