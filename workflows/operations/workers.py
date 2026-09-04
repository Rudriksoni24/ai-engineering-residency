from __future__ import annotations

from workflows.contracts.state import (
    WorkflowState,
)
from workflows.coordination.contracts import (
    WorkerResult,
)
from workflows.resilience.contracts import (
    RecoverableWorkflowError,
)


class AccountWorker:
    @property
    def name(self) -> str:
        return "account"

    def run(
        self,
        task: str,
        state: WorkflowState,
    ) -> WorkerResult:
        return WorkerResult(
            worker_name=self.name,
            output={
                "account_id": "ACC001",
                "status": "active",
            },
        )


class TransactionWorker:
    def __init__(
        self,
        *,
        transient_failures: int = 0,
    ) -> None:
        self._transient_failures = (
            transient_failures
        )

        self.calls = 0

    @property
    def name(self) -> str:
        return "transaction"

    def run(
        self,
        task: str,
        state: WorkflowState,
    ) -> WorkerResult:
        self.calls += 1

        if (
            self.calls
            <= self._transient_failures
        ):
            raise (
                RecoverableWorkflowError(
                    "Temporary transaction "
                    "service failure."
                )
            )

        return WorkerResult(
            worker_name=self.name,
            output={
                "transaction_id": "TXN9001",
                "status": "completed",
            },
        )


class KnowledgeWorker:
    @property
    def name(self) -> str:
        return "knowledge"

    def run(
        self,
        task: str,
        state: WorkflowState,
    ) -> WorkerResult:
        return WorkerResult(
            worker_name=self.name,
            output={
                "explanation": (
                    "Banking policy "
                    "explanation completed."
                ),
            },
        )


class FallbackWorker:
    @property
    def name(self) -> str:
        return "fallback"

    def run(
        self,
        task: str,
        state: WorkflowState,
    ) -> WorkerResult:
        return WorkerResult(
            worker_name=self.name,
            output={
                "message": (
                    "No specialized worker "
                    "matched the request."
                ),
            },
        )