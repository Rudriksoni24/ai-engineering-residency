import pytest

from workflows.contracts.state import WorkflowState
from workflows.graph.contracts import WorkflowTraceEventType
from workflows.graph.engine import (
    END,
    WorkflowGraph,
    WorkflowGraphEngine,
    WorkflowGraphError,
    WorkflowGraphValidationError,
    WorkflowRoutingError,
)


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
    }
    return state


def transaction_worker(
    state: WorkflowState,
) -> WorkflowState:
    state.result = {
        "worker": "transaction_worker",
    }
    return state


def fallback(
    state: WorkflowState,
) -> WorkflowState:
    state.result = {
        "worker": "fallback",
    }
    return state


def build_valid_graph() -> WorkflowGraph:
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


def make_state(
    request: str,
) -> WorkflowState:
    return WorkflowState.create(
        {
            "request": request,
        },
        workflow_id="workflow-test-001",
    )


def test_account_request_routes_to_account_worker() -> None:
    graph = build_valid_graph()
    engine = WorkflowGraphEngine(graph)

    state = make_state(
        "Show account ACC001"
    )

    result = engine.run(state)

    assert result.context["task_type"] == "account"
    assert result.result == {
        "worker": "account_worker",
    }


def test_transaction_request_routes_to_transaction_worker() -> None:
    graph = build_valid_graph()
    engine = WorkflowGraphEngine(graph)

    state = make_state(
        "Show transaction TXN9001"
    )

    result = engine.run(state)

    assert result.context["task_type"] == "transaction"
    assert result.result == {
        "worker": "transaction_worker",
    }


def test_unknown_request_routes_to_fallback() -> None:
    graph = build_valid_graph()
    engine = WorkflowGraphEngine(graph)

    state = make_state(
        "Tell me a joke"
    )

    result = engine.run(state)

    assert result.context["task_type"] == "unsupported"
    assert result.result == {
        "worker": "fallback",
    }


def test_trace_records_node_execution() -> None:
    graph = build_valid_graph()
    engine = WorkflowGraphEngine(graph)

    engine.run(
        make_state("Show account ACC001")
    )

    started_nodes = [
        event.node
        for event in engine.trace
        if event.event_type
        is WorkflowTraceEventType.NODE_STARTED
    ]

    assert started_nodes == [
        "classify",
        "account_worker",
    ]


def test_trace_records_conditional_route() -> None:
    graph = build_valid_graph()
    engine = WorkflowGraphEngine(graph)

    engine.run(
        make_state("Show transaction TXN9001")
    )

    routing_events = [
        event
        for event in engine.trace
        if event.event_type
        is WorkflowTraceEventType.ROUTE_SELECTED
    ]

    assert routing_events[0].source == "classify"
    assert routing_events[0].destination == "transaction_worker"
    assert routing_events[0].route == "transaction"


def test_trace_ends_with_workflow_completed() -> None:
    graph = build_valid_graph()
    engine = WorkflowGraphEngine(graph)

    engine.run(
        make_state("Show account ACC001")
    )

    assert (
        engine.trace[-1].event_type
        is WorkflowTraceEventType.WORKFLOW_COMPLETED
    )

    assert engine.trace[-1].destination == END


def test_graph_requires_start_node() -> None:
    graph = WorkflowGraph()

    graph.add_node(
        "worker",
        account_worker,
    )

    graph.add_edge(
        "worker",
        END,
    )

    with pytest.raises(
        WorkflowGraphValidationError,
        match="requires a start node",
    ):
        graph.validate()


def test_start_node_must_be_registered() -> None:
    graph = WorkflowGraph()

    graph.set_start("missing")

    with pytest.raises(
        WorkflowGraphValidationError,
        match="is not registered",
    ):
        graph.validate()


def test_duplicate_node_is_rejected() -> None:
    graph = WorkflowGraph()

    graph.add_node(
        "worker",
        account_worker,
    )

    with pytest.raises(
        WorkflowGraphValidationError,
        match="already registered",
    ):
        graph.add_node(
            "worker",
            account_worker,
        )


def test_edge_source_must_exist() -> None:
    graph = WorkflowGraph()

    graph.add_node(
        "worker",
        account_worker,
    )

    graph.set_start("worker")

    graph.add_edge(
        "missing",
        END,
    )

    graph.add_edge(
        "worker",
        END,
    )

    with pytest.raises(
        WorkflowGraphValidationError,
        match="Edge source",
    ):
        graph.validate()


def test_edge_destination_must_exist() -> None:
    graph = WorkflowGraph()

    graph.add_node(
        "worker",
        account_worker,
    )

    graph.set_start("worker")

    graph.add_edge(
        "worker",
        "missing",
    )

    with pytest.raises(
        WorkflowGraphValidationError,
        match="Edge destination",
    ):
        graph.validate()


def test_node_cannot_have_conflicting_routes() -> None:
    graph = WorkflowGraph()

    graph.add_node(
        "worker",
        account_worker,
    )

    graph.add_edge(
        "worker",
        END,
    )

    with pytest.raises(
        WorkflowGraphValidationError,
        match="already has outgoing routing",
    ):
        graph.add_conditional_edges(
            "worker",
            route_request,
            {
                "account": END,
            },
        )


def test_unknown_router_result_is_rejected() -> None:
    graph = WorkflowGraph()

    def bad_router(
        state: WorkflowState,
    ) -> str:
        return "does-not-exist"

    graph.add_node(
        "classify",
        classify_request,
    )

    graph.set_start("classify")

    graph.add_conditional_edges(
        "classify",
        bad_router,
        {
            "account": END,
        },
    )

    engine = WorkflowGraphEngine(graph)

    with pytest.raises(
        WorkflowRoutingError,
        match="unknown route",
    ):
        engine.run(
            make_state("account")
        )


def test_graph_protects_against_infinite_execution() -> None:
    graph = WorkflowGraph()

    def passthrough(
        state: WorkflowState,
    ) -> WorkflowState:
        return state

    graph.add_node(
        "a",
        passthrough,
    )

    graph.add_node(
        "b",
        passthrough,
    )

    graph.set_start("a")

    graph.add_edge(
        "a",
        "b",
    )

    graph.add_edge(
        "b",
        "a",
    )

    engine = WorkflowGraphEngine(
        graph,
        max_steps=4,
    )

    with pytest.raises(
        WorkflowGraphError,
        match="maximum graph steps",
    ):
        engine.run(
            make_state("test")
        )