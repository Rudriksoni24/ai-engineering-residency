from __future__ import annotations

from workflows.contracts.state import (
    WorkflowState,
)
from workflows.coordination.contracts import (
    DelegationRequest,
)


class OperationsCoordinator:
    def coordinate(
        self,
        state: WorkflowState,
    ) -> list[DelegationRequest]:
        request = str(
            state.input.get(
                "request",
                "",
            )
        )

        normalized = request.lower()

        delegations: list[
            DelegationRequest
        ] = []

        if "account" in normalized:
            delegations.append(
                DelegationRequest(
                    worker_name="account",
                    task=request,
                )
            )

        if (
            "transaction" in normalized
            or "transfer" in normalized
            or "txn" in normalized
        ):
            delegations.append(
                DelegationRequest(
                    worker_name="transaction",
                    task=request,
                )
            )

        if (
            "explain" in normalized
            or "policy" in normalized
            or "knowledge" in normalized
        ):
            delegations.append(
                DelegationRequest(
                    worker_name="knowledge",
                    task=request,
                )
            )

        if not delegations:
            delegations.append(
                DelegationRequest(
                    worker_name="fallback",
                    task=request,
                )
            )

        return delegations