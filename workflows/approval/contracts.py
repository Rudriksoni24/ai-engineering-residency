from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    workflow_id: str
    action: str
    reason: str
    status: ApprovalStatus
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class ApprovalError(ValueError):
    pass


class ApprovalNotFoundError(
    ApprovalError
):
    pass


class ApprovalAlreadyDecidedError(
    ApprovalError
):
    pass


class WorkflowApprovalPendingError(
    ApprovalError
):
    pass


class WorkflowApprovalRejectedError(
    ApprovalError
):
    pass