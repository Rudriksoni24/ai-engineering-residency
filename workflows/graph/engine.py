from __future__ import annotations

from workflows.contracts.state import WorkflowState
from workflows.graph.contracts import (
    ConditionalWorkflowEdge,
    WorkflowEdge,
    WorkflowNode,
    WorkflowTraceEvent,
    WorkflowTraceEventType,
)

END = "__end__"


class WorkflowGraphError(ValueError):
    pass


class WorkflowGraphValidationError(WorkflowGraphError):
    pass


class WorkflowRoutingError(WorkflowGraphError):
    pass


class WorkflowGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, WorkflowNode] = {}
        self._edges: dict[str, WorkflowEdge] = {}
        self._conditional_edges: dict[str, ConditionalWorkflowEdge] = {}
        self._start_node: str | None = None

    @property
    def start_node(self) -> str | None:
        return self._start_node

    @property
    def node_names(self) -> tuple[str, ...]:
        return tuple(self._nodes)

    def add_node(
        self,
        name: str,
        handler,
    ) -> None:
        if not name:
            raise WorkflowGraphValidationError(
                "Workflow node name cannot be empty."
            )

        if name == END:
            raise WorkflowGraphValidationError(
                f"{END!r} is reserved as the terminal node."
            )

        if name in self._nodes:
            raise WorkflowGraphValidationError(
                f"Workflow node {name!r} is already registered."
            )

        self._nodes[name] = WorkflowNode(
            name=name,
            handler=handler,
        )

    def set_start(self, node_name: str) -> None:
        self._start_node = node_name

    def add_edge(
        self,
        source: str,
        destination: str,
    ) -> None:
        self._ensure_source_has_no_route(source)

        self._edges[source] = WorkflowEdge(
            source=source,
            destination=destination,
        )

    def add_conditional_edges(
        self,
        source: str,
        router,
        routes: dict[str, str],
    ) -> None:
        self._ensure_source_has_no_route(source)

        if not routes:
            raise WorkflowGraphValidationError(
                "Conditional routing requires at least one route."
            )

        self._conditional_edges[source] = ConditionalWorkflowEdge(
            source=source,
            router=router,
            routes=dict(routes),
        )

    def get_node(self, name: str) -> WorkflowNode:
        try:
            return self._nodes[name]
        except KeyError as exc:
            raise WorkflowGraphError(
                f"Unknown workflow node {name!r}."
            ) from exc

    def next_node(
        self,
        current_node: str,
        state: WorkflowState,
    ) -> tuple[str, str | None]:
        edge = self._edges.get(current_node)

        if edge is not None:
            return edge.destination, None

        conditional = self._conditional_edges.get(current_node)

        if conditional is not None:
            route = conditional.router(state)

            try:
                destination = conditional.routes[route]
            except KeyError as exc:
                raise WorkflowRoutingError(
                    f"Router for node {current_node!r} returned "
                    f"unknown route {route!r}."
                ) from exc

            return destination, route

        raise WorkflowRoutingError(
            f"Node {current_node!r} has no outgoing route."
        )

    def validate(self) -> None:
        if self._start_node is None:
            raise WorkflowGraphValidationError(
                "Workflow graph requires a start node."
            )

        if self._start_node not in self._nodes:
            raise WorkflowGraphValidationError(
                f"Start node {self._start_node!r} is not registered."
            )

        for source, edge in self._edges.items():
            self._validate_registered_source(source)
            self._validate_destination(edge.destination)

        for source, conditional in self._conditional_edges.items():
            self._validate_registered_source(source)

            for destination in conditional.routes.values():
                self._validate_destination(destination)

        for node_name in self._nodes:
            if (
                node_name not in self._edges
                and node_name not in self._conditional_edges
            ):
                raise WorkflowGraphValidationError(
                    f"Node {node_name!r} has no outgoing route."
                )

    def _ensure_source_has_no_route(
        self,
        source: str,
    ) -> None:
        if source in self._edges or source in self._conditional_edges:
            raise WorkflowGraphValidationError(
                f"Node {source!r} already has outgoing routing."
            )

    def _validate_registered_source(
        self,
        source: str,
    ) -> None:
        if source not in self._nodes:
            raise WorkflowGraphValidationError(
                f"Edge source {source!r} is not a registered node."
            )

    def _validate_destination(
        self,
        destination: str,
    ) -> None:
        if destination == END:
            return

        if destination not in self._nodes:
            raise WorkflowGraphValidationError(
                f"Edge destination {destination!r} "
                "is not a registered node."
            )


class WorkflowGraphEngine:
    def __init__(
        self,
        graph: WorkflowGraph,
        *,
        max_steps: int = 100,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than zero.")

        graph.validate()

        self._graph = graph
        self._max_steps = max_steps
        self._trace: list[WorkflowTraceEvent] = []

    @property
    def trace(self) -> tuple[WorkflowTraceEvent, ...]:
        return tuple(self._trace)

    def run(
        self,
        state: WorkflowState,
    ) -> WorkflowState:
        current_node = self._graph.start_node

        if current_node is None:
            raise WorkflowGraphError(
                "Validated graph unexpectedly has no start node."
            )

        steps = 0

        while current_node != END:
            if steps >= self._max_steps:
                raise WorkflowGraphError(
                    f"Workflow exceeded maximum graph steps "
                    f"({self._max_steps})."
                )

            node = self._graph.get_node(current_node)

            self._trace.append(
                WorkflowTraceEvent(
                    event_type=WorkflowTraceEventType.NODE_STARTED,
                    node=current_node,
                )
            )

            state = node.handler(state)

            self._trace.append(
                WorkflowTraceEvent(
                    event_type=WorkflowTraceEventType.NODE_COMPLETED,
                    node=current_node,
                )
            )

            next_node, route = self._graph.next_node(
                current_node,
                state,
            )

            self._trace.append(
                WorkflowTraceEvent(
                    event_type=WorkflowTraceEventType.ROUTE_SELECTED,
                    source=current_node,
                    destination=next_node,
                    route=route,
                )
            )

            current_node = next_node
            steps += 1

        self._trace.append(
            WorkflowTraceEvent(
                event_type=WorkflowTraceEventType.WORKFLOW_COMPLETED,
                destination=END,
            )
        )

        return state