from workflows.contracts.state import (
    WorkflowState,
)
from workflows.coordination.contracts import (
    CoordinationTraceEventType,
    WorkerResult,
)
from workflows.coordination.coordinator import (
    BankingCoordinatorAgent,
)
from workflows.coordination.engine import (
    CoordinationEngine,
)
from workflows.coordination.registry import (
    WorkerRegistry,
)


class AccountWorkerAgent:
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
                "task": task,
            },
        )


class TransactionWorkerAgent:
    @property
    def name(self) -> str:
        return "transaction"

    def run(
        self,
        task: str,
        state: WorkflowState,
    ) -> WorkerResult:
        return WorkerResult(
            worker_name=self.name,
            output={
                "transaction_id": "TXN9001",
                "status": "completed",
                "task": task,
            },
        )


class KnowledgeWorkerAgent:
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
                    "Knowledge worker handled "
                    "the explanation request."
                ),
                "task": task,
            },
        )


class FallbackWorkerAgent:
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
                "task": task,
            },
        )


def build_registry() -> WorkerRegistry:
    registry = WorkerRegistry()

    registry.register(
        AccountWorkerAgent()
    )

    registry.register(
        TransactionWorkerAgent()
    )

    registry.register(
        KnowledgeWorkerAgent()
    )

    registry.register(
        FallbackWorkerAgent()
    )

    return registry


def main() -> None:
    state = WorkflowState.create(
        {
            "request": (
                "Show account ACC001 and "
                "explain its banking policy"
            ),
        },
        workflow_id=(
            "workflow-multi-agent-demo-001"
        ),
    )

    engine = CoordinationEngine(
        BankingCoordinatorAgent(),
        build_registry(),
    )

    results = engine.run(state)

    print("Worker results")
    print()

    for result in results:
        print(
            f"{result.worker_name}: "
            f"{result.output}"
        )

    print()
    print("Workflow context")
    print(
        state.context[
            "worker_results"
        ]
    )

    print()
    print("Coordination trace")

    for index, event in enumerate(
        engine.trace,
        start=1,
    ):
        print(
            f"{index}. "
            f"type={event.event_type.value}, "
            f"worker={event.worker_name}"
        )

    selected = [
        event.worker_name
        for event in engine.trace
        if event.event_type
        is CoordinationTraceEventType
        .DELEGATION_SELECTED
    ]

    print()
    print(
        f"Delegated workers: {selected}"
    )


if __name__ == "__main__":
    main()