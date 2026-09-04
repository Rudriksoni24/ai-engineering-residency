from __future__ import annotations

from typing import Any
from uuid import uuid4

from workflows.approval.contracts import (
    ApprovalAlreadyDecidedError,
    ApprovalNotFoundError,
    ApprovalRequest,
    ApprovalStatus,
)
from workflows.contracts.state import (
    WorkflowState,
)
from workflows.persistence.contracts import (
    CheckpointStore,
    WorkflowCheckpoint,
)

APPROVAL_CONTEXT_KEY = "approval"


class ApprovalManager:
    def __init__(
        self,
        checkpoint_store: CheckpointStore,
    ) -> None:
        self._checkpoint_store = (
            checkpoint_store
        )

    def request_approval(
        self,
        state: WorkflowState,
        *,
        next_node: str,
        action: str,
        reason: str,
        metadata: dict[str, Any] | None = None,
        approval_id: str | None = None,
    ) -> ApprovalRequest:
        request = ApprovalRequest(
            approval_id=(
                approval_id
                or str(uuid4())
            ),
            workflow_id=state.workflow_id,
            action=action,
            reason=reason,
            status=ApprovalStatus.PENDING,
            metadata=dict(
                metadata or {}
            ),
        )

        state.context[
            APPROVAL_CONTEXT_KEY
        ] = self._to_dict(request)

        self._checkpoint_store.save(
            WorkflowCheckpoint(
                workflow_id=state.workflow_id,
                state=state,
                next_node=next_node,
                completed=False,
            )
        )

        return request

    def get(
        self,
        workflow_id: str,
    ) -> ApprovalRequest | None:
        checkpoint = (
            self._checkpoint_store.load(
                workflow_id
            )
        )

        if checkpoint is None:
            return None

        approval_data = (
            checkpoint.state.context.get(
                APPROVAL_CONTEXT_KEY
            )
        )

        if approval_data is None:
            return None

        if not isinstance(
            approval_data,
            dict,
        ):
            raise ApprovalNotFoundError(
                "Stored approval metadata "
                "is invalid."
            )

        return self._from_dict(
            approval_data
        )

    def approve(
        self,
        workflow_id: str,
    ) -> ApprovalRequest:
        return self._decide(
            workflow_id,
            ApprovalStatus.APPROVED,
        )

    def reject(
        self,
        workflow_id: str,
    ) -> ApprovalRequest:
        return self._decide(
            workflow_id,
            ApprovalStatus.REJECTED,
        )

    def _decide(
        self,
        workflow_id: str,
        decision: ApprovalStatus,
    ) -> ApprovalRequest:
        checkpoint = (
            self._checkpoint_store.load(
                workflow_id
            )
        )

        if checkpoint is None:
            raise ApprovalNotFoundError(
                f"No workflow checkpoint "
                f"found for {workflow_id!r}."
            )

        approval_data = (
            checkpoint.state.context.get(
                APPROVAL_CONTEXT_KEY
            )
        )

        if not isinstance(
            approval_data,
            dict,
        ):
            raise ApprovalNotFoundError(
                f"No approval request found "
                f"for workflow "
                f"{workflow_id!r}."
            )

        current = self._from_dict(
            approval_data
        )

        if (
            current.status
            is not ApprovalStatus.PENDING
        ):
            raise (
                ApprovalAlreadyDecidedError(
                    f"Approval "
                    f"{current.approval_id!r} "
                    f"is already "
                    f"{current.status.value!r}."
                )
            )

        updated = ApprovalRequest(
            approval_id=current.approval_id,
            workflow_id=(
                current.workflow_id
            ),
            action=current.action,
            reason=current.reason,
            status=decision,
            metadata=dict(
                current.metadata
            ),
        )

        checkpoint.state.context[
            APPROVAL_CONTEXT_KEY
        ] = self._to_dict(updated)

        self._checkpoint_store.save(
            WorkflowCheckpoint(
                workflow_id=(
                    checkpoint.workflow_id
                ),
                state=checkpoint.state,
                next_node=(
                    checkpoint.next_node
                ),
                completed=(
                    checkpoint.completed
                ),
            )
        )

        return updated

    @staticmethod
    def _to_dict(
        request: ApprovalRequest,
    ) -> dict[str, Any]:
        return {
            "approval_id": (
                request.approval_id
            ),
            "workflow_id": (
                request.workflow_id
            ),
            "action": request.action,
            "reason": request.reason,
            "status": (
                request.status.value
            ),
            "metadata": dict(
                request.metadata
            ),
        }

    @staticmethod
    def _from_dict(
        data: dict[str, Any],
    ) -> ApprovalRequest:
        metadata = data.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            raise ApprovalNotFoundError(
                "Stored approval metadata "
                "must be a dictionary."
            )

        return ApprovalRequest(
            approval_id=str(
                data["approval_id"]
            ),
            workflow_id=str(
                data["workflow_id"]
            ),
            action=str(
                data["action"]
            ),
            reason=str(
                data["reason"]
            ),
            status=ApprovalStatus(
                data["status"]
            ),
            metadata=dict(metadata),
        )