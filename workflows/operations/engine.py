from __future__ import annotations

from collections.abc import Callable

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
from workflows.coordination.contracts import (
    CoordinatorAgent,
    WorkerResult,
)
from workflows.coordination.registry import (
    WorkerRegistry,
)
from workflows.core.state_machine import (
    WorkflowStateMachine,
)
from workflows.persistence.contracts import (
    CheckpointStore,
    WorkflowCheckpoint,
)
from workflows.resilience.contracts import (
    RecoverableWorkflowError,
    RetryExhaustedError,
)
from workflows.resilience.policy import (
    RetryPolicy,
)
from workflows.tracing.contracts import (
    WorkflowEvent,
    WorkflowEventType,
)
from workflows.tracing.recorder import (
    WorkflowTraceRecorder,
)

Sleeper = Callable[[float], None]

COORDINATE_NODE = "coordinate"
EXECUTE_NODE = "execute"
END_NODE = "__end__"


class MultiAgentOperationsEngine:
    def __init__(
        self,
        *,
        checkpoint_store: CheckpointStore,
        coordinator: CoordinatorAgent,
        worker_registry: WorkerRegistry,
        approval_manager: ApprovalManager,
        trace_recorder: WorkflowTraceRecorder,
        retry_policy: RetryPolicy,
        sleeper: Sleeper,
    ) -> None:
        self._checkpoint_store = (
            checkpoint_store
        )

        self._coordinator = coordinator

        self._worker_registry = (
            worker_registry
        )

        self._approval_manager = (
            approval_manager
        )

        self._trace = trace_recorder

        self._retry_policy = retry_policy

        self._sleeper = sleeper

    @property
    def trace(
        self,
    ) -> tuple[
        WorkflowEvent,
        ...
    ]:
        return self._trace.events

    def start(
        self,
        state: WorkflowState,
    ) -> WorkflowState:
        self._trace.clear()

        self._record(
            WorkflowEventType
            .WORKFLOW_STARTED,
            state,
        )

        machine = WorkflowStateMachine(
            state
        )

        self._transition(
            machine,
            WorkflowStatus.PLANNING,
        )

        self._save_checkpoint(
            state,
            COORDINATE_NODE,
        )

        return self._run_from(
            state,
            COORDINATE_NODE,
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

        state = checkpoint.state

        if checkpoint.completed:
            return state

        approval = (
            self._approval_manager.get(
                workflow_id
            )
        )

        if (
            approval is not None
            and approval.status
            is ApprovalStatus.PENDING
        ):
            raise (
                WorkflowApprovalPendingError(
                    f"Workflow "
                    f"{workflow_id!r} "
                    "is waiting for approval."
                )
            )

        if (
            approval is not None
            and approval.status
            is ApprovalStatus.REJECTED
        ):
            self._record(
                WorkflowEventType
                .APPROVAL_REJECTED,
                state,
                message=(
                    "Protected operation "
                    "was rejected."
                ),
            )

            raise (
                WorkflowApprovalRejectedError(
                    f"Workflow "
                    f"{workflow_id!r} "
                    "was rejected."
                )
            )

        if (
            approval is not None
            and approval.status
            is ApprovalStatus.APPROVED
        ):
            self._record(
                WorkflowEventType
                .APPROVAL_GRANTED,
                state,
                message=(
                    "Protected operation "
                    "was approved."
                ),
            )

        return self._run_from(
            state,
            checkpoint.next_node,
        )

    def approve(
        self,
        workflow_id: str,
    ) -> None:
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

        self._approval_manager.approve(
            workflow_id
        )

        self._record(
            WorkflowEventType
            .APPROVAL_GRANTED,
            checkpoint.state,
        )

    def reject(
        self,
        workflow_id: str,
    ) -> None:
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

        self._approval_manager.reject(
            workflow_id
        )

        self._record(
            WorkflowEventType
            .APPROVAL_REJECTED,
            checkpoint.state,
        )

    def _run_from(
        self,
        state: WorkflowState,
        current_node: str,
    ) -> WorkflowState:
        if current_node == COORDINATE_NODE:
            state = self._coordinate(
                state
            )

            approval = (
                self._approval_manager.get(
                    state.workflow_id
                )
            )

            if (
                approval is not None
                and approval.status
                is ApprovalStatus.PENDING
            ):
                return state

            current_node = EXECUTE_NODE

        if current_node == EXECUTE_NODE:
            state = self._execute(
                state
            )

        return state

    def _coordinate(
        self,
        state: WorkflowState,
    ) -> WorkflowState:
        self._record(
            WorkflowEventType
            .NODE_STARTED,
            state,
            node=COORDINATE_NODE,
        )

        delegations = (
            self._coordinator.coordinate(
                state
            )
        )

        state.context[
            "delegations"
        ] = [
            {
                "worker_name": (
                    delegation.worker_name
                ),
                "task": delegation.task,
            }
            for delegation in delegations
        ]

        for delegation in delegations:
            self._record(
                WorkflowEventType
                .WORKER_DELEGATED,
                state,
                node=COORDINATE_NODE,
                worker_name=(
                    delegation.worker_name
                ),
                metadata={
                    "task": (
                        delegation.task
                    ),
                },
            )

        self._record(
            WorkflowEventType
            .NODE_COMPLETED,
            state,
            node=COORDINATE_NODE,
        )

        self._record(
            WorkflowEventType
            .ROUTE_SELECTED,
            state,
            source=COORDINATE_NODE,
            destination=EXECUTE_NODE,
        )

        machine = WorkflowStateMachine(
            state
        )

        if (
            state.status
            is WorkflowStatus.PLANNING
        ):
            self._transition(
                machine,
                WorkflowStatus.EXECUTING,
            )

        self._save_checkpoint(
            state,
            EXECUTE_NODE,
        )

        if self._requires_approval(
            state
        ):
            approval = (
                self._approval_manager
                .get(state.workflow_id)
            )

            if approval is None:
                self._approval_manager.request_approval(
                    state,
                    next_node=(
                        EXECUTE_NODE
                    ),
                    action=(
                        "execute_transaction"
                    ),
                    reason=(
                        "Sensitive transaction "
                        "requires human "
                        "approval."
                    ),
                    metadata={
                        "delegations": (
                            state.context[
                                "delegations"
                            ]
                        ),
                    },
                )

                self._record(
                    WorkflowEventType
                    .APPROVAL_REQUESTED,
                    state,
                    node=EXECUTE_NODE,
                )

                self._record(
                    WorkflowEventType
                    .WORKFLOW_SUSPENDED,
                    state,
                    node=EXECUTE_NODE,
                )

                return state

        return self._execute(
            state
        )

    def _execute(
        self,
        state: WorkflowState,
    ) -> WorkflowState:
        approval = (
            self._approval_manager.get(
                state.workflow_id
            )
        )

        if (
            approval is not None
            and approval.status
            is ApprovalStatus.PENDING
        ):
            raise (
                WorkflowApprovalPendingError(
                    f"Workflow "
                    f"{state.workflow_id!r} "
                    "is waiting for approval."
                )
            )

        if (
            approval is not None
            and approval.status
            is ApprovalStatus.REJECTED
        ):
            raise (
                WorkflowApprovalRejectedError(
                    f"Workflow "
                    f"{state.workflow_id!r} "
                    "was rejected."
                )
            )

        self._record(
            WorkflowEventType
            .NODE_STARTED,
            state,
            node=EXECUTE_NODE,
        )

        delegation_data = (
            state.context.get(
                "delegations",
                [],
            )
        )

        results: list[
            WorkerResult
        ] = []

        try:
            for item in delegation_data:
                if not isinstance(
                    item,
                    dict,
                ):
                    raise ValueError(  # noqa: TRY004
                        "Invalid delegation "
                        "data."
                    )

                worker_name = str(
                    item["worker_name"]
                )

                task = str(
                    item["task"]
                )

                worker = (
                    self._worker_registry.get(
                        worker_name
                    )
                )

                result = (
                    self._execute_worker(
                        state=state,
                        worker_name=(
                            worker_name
                        ),
                        task=task,
                        worker=worker,
                    )
                )

                results.append(result)

        except Exception as exc:
            machine = WorkflowStateMachine(
                state
            )

            if (
                state.status
                is WorkflowStatus.EXECUTING
            ):
                machine.fail(
                    str(exc)
                )

                self._record(
                    WorkflowEventType
                    .LIFECYCLE_TRANSITION,
                    state,
                    source=(
                        WorkflowStatus
                        .EXECUTING.value
                    ),
                    destination=(
                        WorkflowStatus
                        .FAILED.value
                    ),
                )

            self._record(
                WorkflowEventType
                .WORKFLOW_FAILED,
                state,
                node=EXECUTE_NODE,
                message=str(exc),
            )

            self._save_checkpoint(
                state,
                EXECUTE_NODE,
            )

            raise

        state.context[
            "worker_results"
        ] = [
            {
                "worker_name": (
                    result.worker_name
                ),
                "output": result.output,
            }
            for result in results
        ]

        state.result = state.context[
            "worker_results"
        ]

        self._record(
            WorkflowEventType
            .NODE_COMPLETED,
            state,
            node=EXECUTE_NODE,
        )

        machine = WorkflowStateMachine(
            state
        )

        if (
            state.status
            is WorkflowStatus.EXECUTING
        ):
            machine.complete(
                state.result
            )

            self._record(
                WorkflowEventType
                .LIFECYCLE_TRANSITION,
                state,
                source=(
                    WorkflowStatus
                    .EXECUTING.value
                ),
                destination=(
                    WorkflowStatus
                    .COMPLETED.value
                ),
            )

        self._checkpoint_store.save(
            WorkflowCheckpoint(
                workflow_id=(
                    state.workflow_id
                ),
                state=state,
                next_node=END_NODE,
                completed=True,
            )
        )

        self._record(
            WorkflowEventType
            .CHECKPOINT_SAVED,
            state,
            node=END_NODE,
        )

        self._record(
            WorkflowEventType
            .WORKFLOW_COMPLETED,
            state,
        )

        return state

    def _execute_worker(
        self,
        *,
        state: WorkflowState,
        worker_name: str,
        task: str,
        worker,
    ) -> WorkerResult:
        policy = self._retry_policy

        for attempt in range(
            1,
            policy.max_attempts + 1,
        ):
            self._record(
                WorkflowEventType
                .ATTEMPT_STARTED,
                state,
                node=EXECUTE_NODE,
                worker_name=worker_name,
                attempt=attempt,
            )

            try:
                result = worker.run(
                    task,
                    state,
                )

            except (
                RecoverableWorkflowError
            ) as exc:
                state.context[
                    "retry"
                ] = {
                    "worker_name": (
                        worker_name
                    ),
                    "attempt": attempt,
                    "max_attempts": (
                        policy.max_attempts
                    ),
                    "status": (
                        "retrying"
                    ),
                    "last_error": str(exc),
                    "last_error_type": (
                        type(exc).__name__
                    ),
                }

                self._save_checkpoint(
                    state,
                    EXECUTE_NODE,
                )

                self._record(
                    WorkflowEventType
                    .ATTEMPT_FAILED,
                    state,
                    node=EXECUTE_NODE,
                    worker_name=(
                        worker_name
                    ),
                    attempt=attempt,
                    message=str(exc),
                )

                if (
                    attempt
                    >= policy.max_attempts
                ):
                    state.context[
                        "retry"
                    ][
                        "status"
                    ] = "exhausted"

                    self._save_checkpoint(
                        state,
                        EXECUTE_NODE,
                    )

                    raise (
                        RetryExhaustedError(
                            f"Worker "
                            f"{worker_name!r} "
                            f"failed after "
                            f"{attempt} "
                            f"attempts."
                        )
                    ) from exc

                self._record(
                    WorkflowEventType
                    .RETRY_SCHEDULED,
                    state,
                    node=EXECUTE_NODE,
                    worker_name=(
                        worker_name
                    ),
                    attempt=attempt,
                )

                self._sleeper(
                    policy.delay_seconds
                )

                continue

            if (
                result.worker_name
                != worker_name
            ):
                raise ValueError(
                    "Worker returned result "
                    "for a different worker."
                )

            state.context.pop(
                "retry",
                None,
            )

            self._record(
                WorkflowEventType
                .WORKER_COMPLETED,
                state,
                node=EXECUTE_NODE,
                worker_name=worker_name,
                attempt=attempt,
            )

            return result

        raise RuntimeError(
            "Worker retry loop exited "
            "unexpectedly."
        )

    @staticmethod
    def _requires_approval(
        state: WorkflowState,
    ) -> bool:
        delegations = (
            state.context.get(
                "delegations",
                [],
            )
        )

        return any(
            isinstance(item, dict)
            and item.get(
                "worker_name"
            ) == "transaction"
            for item in delegations
        )

    def _save_checkpoint(
        self,
        state: WorkflowState,
        next_node: str,
    ) -> None:
        self._checkpoint_store.save(
            WorkflowCheckpoint(
                workflow_id=(
                    state.workflow_id
                ),
                state=state,
                next_node=next_node,
                completed=False,
            )
        )

        self._record(
            WorkflowEventType
            .CHECKPOINT_SAVED,
            state,
            node=next_node,
        )

    def _transition(
        self,
        machine: WorkflowStateMachine,
        destination: WorkflowStatus,
    ) -> None:
        source = machine.status

        machine.transition_to(
            destination
        )

        self._record(
            WorkflowEventType
            .LIFECYCLE_TRANSITION,
            machine.state,
            source=source.value,
            destination=(
                destination.value
            ),
        )

    def _record(
        self,
        event_type: WorkflowEventType,
        state: WorkflowState,
        *,
        node: str | None = None,
        worker_name: str | None = None,
        source: str | None = None,
        destination: str | None = None,
        attempt: int | None = None,
        message: str | None = None,
        metadata: dict[
            str,
            object,
        ]
        | None = None,
    ) -> None:
        self._trace.record(
            WorkflowEvent(
                event_type=event_type,
                workflow_id=(
                    state.workflow_id
                ),
                node=node,
                worker_name=(
                    worker_name
                ),
                source=source,
                destination=destination,
                attempt=attempt,
                message=message,
                metadata=metadata,
            )
        )