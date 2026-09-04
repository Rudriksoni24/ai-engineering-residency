from __future__ import annotations

from workflows.contracts.state import WorkflowState
from workflows.graph.engine import (
    END,
    WorkflowGraph,
    WorkflowGraphError,
)
from workflows.persistence.contracts import (
    CheckpointStore,
    WorkflowCheckpoint,
)


class WorkflowCheckpointNotFoundError(
    LookupError
):
    pass


class PersistentWorkflowEngine:
    def __init__(
        self,
        graph: WorkflowGraph,
        checkpoint_store: CheckpointStore,
        *,
        max_steps: int = 100,
    ) -> None:
        if max_steps <= 0:
            raise ValueError(
                "max_steps must be greater than zero."
            )

        graph.validate()

        self._graph = graph
        self._checkpoint_store = checkpoint_store
        self._max_steps = max_steps

    def start(
        self,
        state: WorkflowState,
        *,
        stop_after_steps: int | None = None,
    ) -> WorkflowState:
        start_node = self._graph.start_node

        if start_node is None:
            raise WorkflowGraphError(
                "Validated graph unexpectedly "
                "has no start node."
            )

        self._checkpoint_store.save(
            WorkflowCheckpoint(
                workflow_id=state.workflow_id,
                state=state,
                next_node=start_node,
                completed=False,
            )
        )

        return self._execute(
            state=state,
            current_node=start_node,
            stop_after_steps=stop_after_steps,
        )

    def resume(
        self,
        workflow_id: str,
        *,
        stop_after_steps: int | None = None,
    ) -> WorkflowState:
        checkpoint = self._checkpoint_store.load(
            workflow_id
        )

        if checkpoint is None:
            raise WorkflowCheckpointNotFoundError(
                f"No checkpoint found for workflow "
                f"{workflow_id!r}."
            )

        if checkpoint.completed:
            return checkpoint.state

        return self._execute(
            state=checkpoint.state,
            current_node=checkpoint.next_node,
            stop_after_steps=stop_after_steps,
        )

    def load(
        self,
        workflow_id: str,
    ) -> WorkflowCheckpoint | None:
        return self._checkpoint_store.load(
            workflow_id
        )

    def _execute(
        self,
        *,
        state: WorkflowState,
        current_node: str,
        stop_after_steps: int | None,
    ) -> WorkflowState:
        steps = 0

        while current_node != END:
            if steps >= self._max_steps:
                raise WorkflowGraphError(
                    f"Workflow exceeded maximum "
                    f"graph steps ({self._max_steps})."
                )

            if (
                stop_after_steps is not None
                and steps >= stop_after_steps
            ):
                return state

            node = self._graph.get_node(
                current_node
            )

            state = node.handler(state)

            next_node, _ = self._graph.next_node(
                current_node,
                state,
            )

            is_completed = next_node == END

            self._checkpoint_store.save(
                WorkflowCheckpoint(
                    workflow_id=state.workflow_id,
                    state=state,
                    next_node=next_node,
                    completed=is_completed,
                )
            )

            current_node = next_node
            steps += 1

        return state