from __future__ import annotations

import time
from collections.abc import Callable

from workflows.contracts.state import (
    WorkflowState,
)
from workflows.graph.engine import (
    END,
    WorkflowGraph,
    WorkflowGraphError,
)
from workflows.persistence.contracts import (
    CheckpointStore,
    WorkflowCheckpoint,
)
from workflows.resilience.contracts import (
    RecoverableWorkflowError,
    RetryExhaustedError,
    RetryTraceEvent,
    RetryTraceEventType,
)
from workflows.resilience.policy import (
    RetryPolicy,
)

Sleeper = Callable[[float], None]


class ResilientWorkflowEngine:
    def __init__(
        self,
        graph: WorkflowGraph,
        checkpoint_store: CheckpointStore,
        *,
        retry_policy: RetryPolicy | None = None,
        sleeper: Sleeper = time.sleep,
        max_steps: int = 100,
    ) -> None:
        if max_steps <= 0:
            raise ValueError(
                "max_steps must be greater "
                "than zero."
            )

        graph.validate()

        self._graph = graph
        self._checkpoint_store = (
            checkpoint_store
        )
        self._retry_policy = (
            retry_policy or RetryPolicy()
        )
        self._sleeper = sleeper
        self._max_steps = max_steps

        self._trace: list[
            RetryTraceEvent
        ] = []

    @property
    def trace(
        self,
    ) -> tuple[
        RetryTraceEvent,
        ...
    ]:
        return tuple(self._trace)

    def start(
        self,
        state: WorkflowState,
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
        )

    def resume(
        self,
        workflow_id: str,
    ) -> WorkflowState:
        checkpoint = (
            self._checkpoint_store.load(
                workflow_id
            )
        )

        if checkpoint is None:
            raise LookupError(
                f"No checkpoint found for "
                f"workflow {workflow_id!r}."
            )

        if checkpoint.completed:
            return checkpoint.state

        return self._execute(
            state=checkpoint.state,
            current_node=(
                checkpoint.next_node
            ),
        )

    def _execute(
        self,
        *,
        state: WorkflowState,
        current_node: str,
    ) -> WorkflowState:
        steps = 0

        while current_node != END:
            if steps >= self._max_steps:
                raise WorkflowGraphError(
                    f"Workflow exceeded maximum "
                    f"graph steps "
                    f"({self._max_steps})."
                )

            state = self._execute_node(
                state=state,
                node_name=current_node,
            )

            next_node, _ = (
                self._graph.next_node(
                    current_node,
                    state,
                )
            )

            completed = (
                next_node == END
            )

            self._clear_retry_state(
                state
            )

            self._checkpoint_store.save(
                WorkflowCheckpoint(
                    workflow_id=(
                        state.workflow_id
                    ),
                    state=state,
                    next_node=next_node,
                    completed=completed,
                )
            )

            current_node = next_node
            steps += 1

        return state

    def _execute_node(
        self,
        *,
        state: WorkflowState,
        node_name: str,
    ) -> WorkflowState:
        node = self._graph.get_node(
            node_name
        )

        policy = self._retry_policy

        for attempt in range(
            1,
            policy.max_attempts + 1,
        ):
            self._set_retry_state(
                state=state,
                node_name=node_name,
                attempt=attempt,
                status="running",
            )

            self._checkpoint_current_node(
                state,
                node_name,
            )

            self._trace.append(
                RetryTraceEvent(
                    event_type=(
                        RetryTraceEventType
                        .ATTEMPT_STARTED
                    ),
                    node=node_name,
                    attempt=attempt,
                )
            )

            try:
                updated_state = (
                    node.handler(state)
                )
            except (
                RecoverableWorkflowError
            ) as exc:
                self._record_failure(
                    state=state,
                    node_name=node_name,
                    attempt=attempt,
                    exc=exc,
                    status="retrying",
                )

                self._trace.append(
                    RetryTraceEvent(
                        event_type=(
                            RetryTraceEventType
                            .ATTEMPT_FAILED
                        ),
                        node=node_name,
                        attempt=attempt,
                        error_type=(
                            type(exc).__name__
                        ),
                        error_message=str(exc),
                    )
                )

                if (
                    attempt
                    >= policy.max_attempts
                ):
                    self._set_retry_state(
                        state=state,
                        node_name=node_name,
                        attempt=attempt,
                        status="exhausted",
                        last_error=str(exc),
                        last_error_type=(
                            type(exc).__name__
                        ),
                    )

                    self._checkpoint_current_node(
                        state,
                        node_name,
                    )

                    self._trace.append(
                        RetryTraceEvent(
                            event_type=(
                                RetryTraceEventType
                                .RETRY_EXHAUSTED
                            ),
                            node=node_name,
                            attempt=attempt,
                            error_type=(
                                type(exc).__name__
                            ),
                            error_message=(
                                str(exc)
                            ),
                        )
                    )

                    raise RetryExhaustedError(
                        f"Node {node_name!r} "
                        f"failed after "
                        f"{attempt} attempts."
                    ) from exc

                self._trace.append(
                    RetryTraceEvent(
                        event_type=(
                            RetryTraceEventType
                            .RETRY_SCHEDULED
                        ),
                        node=node_name,
                        attempt=attempt,
                        error_type=(
                            type(exc).__name__
                        ),
                        error_message=str(exc),
                    )
                )

                self._sleeper(
                    policy.delay_seconds
                )

                continue

            except Exception as exc:
                self._record_failure(
                    state=state,
                    node_name=node_name,
                    attempt=attempt,
                    exc=exc,
                    status="terminal_failure",
                )

                self._trace.append(
                    RetryTraceEvent(
                        event_type=(
                            RetryTraceEventType
                            .TERMINAL_FAILURE
                        ),
                        node=node_name,
                        attempt=attempt,
                        error_type=(
                            type(exc).__name__
                        ),
                        error_message=str(exc),
                    )
                )

                raise

            if attempt > 1:
                self._trace.append(
                    RetryTraceEvent(
                        event_type=(
                            RetryTraceEventType
                            .NODE_RECOVERED
                        ),
                        node=node_name,
                        attempt=attempt,
                    )
                )

            self._trace.append(
                RetryTraceEvent(
                    event_type=(
                        RetryTraceEventType
                        .NODE_COMPLETED
                    ),
                    node=node_name,
                    attempt=attempt,
                )
            )

            return updated_state

        raise RuntimeError(
            "Retry loop exited "
            "unexpectedly."
        )

    def _record_failure(
        self,
        *,
        state: WorkflowState,
        node_name: str,
        attempt: int,
        exc: Exception,
        status: str,
    ) -> None:
        self._set_retry_state(
            state=state,
            node_name=node_name,
            attempt=attempt,
            status=status,
            last_error=str(exc),
            last_error_type=(
                type(exc).__name__
            ),
        )

        self._checkpoint_current_node(
            state,
            node_name,
        )

    def _checkpoint_current_node(
        self,
        state: WorkflowState,
        node_name: str,
    ) -> None:
        self._checkpoint_store.save(
            WorkflowCheckpoint(
                workflow_id=state.workflow_id,
                state=state,
                next_node=node_name,
                completed=False,
            )
        )

    def _set_retry_state(
        self,
        *,
        state: WorkflowState,
        node_name: str,
        attempt: int,
        status: str,
        last_error: str | None = None,
        last_error_type: str | None = None,
    ) -> None:
        retry_data: dict[
            str,
            object,
        ] = {
            "node": node_name,
            "attempt": attempt,
            "max_attempts": (
                self._retry_policy
                .max_attempts
            ),
            "status": status,
        }

        if last_error is not None:
            retry_data[
                "last_error"
            ] = last_error

        if last_error_type is not None:
            retry_data[
                "last_error_type"
            ] = last_error_type

        state.context[
            "retry"
        ] = retry_data

    @staticmethod
    def _clear_retry_state(
        state: WorkflowState,
    ) -> None:
        state.context.pop(
            "retry",
            None,
        )