from __future__ import annotations

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
)
from workflows.persistence.engine import (
    PersistentWorkflowEngine,
)


class ApprovalWorkflowEngine:
    def __init__(
        self,
        workflow_engine: (
            PersistentWorkflowEngine
        ),
        approval_manager: ApprovalManager,
    ) -> None:
        self._workflow_engine = (
            workflow_engine
        )
        self._approval_manager = (
            approval_manager
        )

    def resume(
        self,
        workflow_id: str,
    ) -> WorkflowState:
        approval = (
            self._approval_manager.get(
                workflow_id
            )
        )

        if approval is None:
            return (
                self._workflow_engine.resume(
                    workflow_id
                )
            )

        if (
            approval.status
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
            approval.status
            is ApprovalStatus.REJECTED
        ):
            raise (
                WorkflowApprovalRejectedError(
                    f"Workflow "
                    f"{workflow_id!r} "
                    "was rejected and cannot "
                    "execute the protected "
                    "operation."
                )
            )

        return self._workflow_engine.resume(
            workflow_id
        )