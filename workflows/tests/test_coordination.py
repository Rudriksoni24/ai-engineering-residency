import pytest

from workflows.contracts.state import (
    WorkflowState,
)
from workflows.coordination.contracts import (
    CoordinationTraceEventType,
    DelegationRequest,
    WorkerResult,
)
from workflows.coordination.coordinator import (
    BankingCoordinatorAgent,
)
from workflows.coordination.engine import (
    CoordinationEngine,
)
from workflows.coordination.registry import (
    WorkerAlreadyRegisteredError,
    WorkerNotFoundError,
    WorkerRegistry,
)


class RecordingWorker:
    def __init__(
        self,
        name: str,
        output: object,
    ) -> None:
        self._name = name
        self._output = output
        self.calls: list[str] = []

    @property
    def name(self) -> str:
        return self._name

    def run(
        self,
        task: str,
        state: WorkflowState,
    ) -> WorkerResult:
        self.calls.append(task)

        return WorkerResult(
            worker_name=self.name,
            output=self._output,
        )


class StaticCoordinator:
    def __init__(
        self,
        delegations: list[
            DelegationRequest
        ],
    ) -> None:
        self._delegations = delegations

    def coordinate(
        self,
        state: WorkflowState,
    ) -> list[DelegationRequest]:
        return list(self._delegations)


def make_state(
    request: str,
) -> WorkflowState:
    return WorkflowState.create(
        {
            "request": request,
        },
        workflow_id="workflow-test-001",
    )


def test_account_request_selects_account_worker() -> None:
    coordinator = (
        BankingCoordinatorAgent()
    )

    state = make_state(
        "Show account ACC001"
    )

    delegations = (
        coordinator.coordinate(state)
    )

    assert delegations == [
        DelegationRequest(
            worker_name="account",
            task="Show account ACC001",
        )
    ]


def test_transaction_request_selects_transaction_worker() -> None:
    coordinator = (
        BankingCoordinatorAgent()
    )

    state = make_state(
        "Show transaction TXN9001"
    )

    delegations = (
        coordinator.coordinate(state)
    )

    assert [
        item.worker_name
        for item in delegations
    ] == [
        "transaction",
    ]


def test_unknown_request_selects_fallback() -> None:
    coordinator = (
        BankingCoordinatorAgent()
    )

    state = make_state(
        "Tell me a joke"
    )

    delegations = (
        coordinator.coordinate(state)
    )

    assert [
        item.worker_name
        for item in delegations
    ] == [
        "fallback",
    ]


def test_multiple_workers_can_be_selected() -> None:
    coordinator = (
        BankingCoordinatorAgent()
    )

    state = make_state(
        (
            "Show account ACC001 and "
            "explain the policy"
        )
    )

    delegations = (
        coordinator.coordinate(state)
    )

    assert [
        item.worker_name
        for item in delegations
    ] == [
        "account",
        "knowledge",
    ]


def test_coordination_engine_executes_selected_worker() -> None:
    account = RecordingWorker(
        "account",
        {
            "account_id": "ACC001",
        },
    )

    registry = WorkerRegistry()
    registry.register(account)

    coordinator = StaticCoordinator(
        [
            DelegationRequest(
                worker_name="account",
                task="Get ACC001",
            )
        ]
    )

    engine = CoordinationEngine(
        coordinator,
        registry,
    )

    results = engine.run(
        make_state("unused")
    )

    assert account.calls == [
        "Get ACC001",
    ]

    assert results == [
        WorkerResult(
            worker_name="account",
            output={
                "account_id": "ACC001",
            },
        )
    ]


def test_multiple_workers_execute_independently() -> None:
    account = RecordingWorker(
        "account",
        "account-result",
    )

    knowledge = RecordingWorker(
        "knowledge",
        "knowledge-result",
    )

    registry = WorkerRegistry()
    registry.register(account)
    registry.register(knowledge)

    coordinator = StaticCoordinator(
        [
            DelegationRequest(
                worker_name="account",
                task="account task",
            ),
            DelegationRequest(
                worker_name="knowledge",
                task="knowledge task",
            ),
        ]
    )

    engine = CoordinationEngine(
        coordinator,
        registry,
    )

    results = engine.run(
        make_state("unused")
    )

    assert account.calls == [
        "account task",
    ]

    assert knowledge.calls == [
        "knowledge task",
    ]

    assert [
        result.worker_name
        for result in results
    ] == [
        "account",
        "knowledge",
    ]


def test_worker_results_are_added_to_workflow_context() -> None:
    worker = RecordingWorker(
        "account",
        {
            "value": 42,
        },
    )

    registry = WorkerRegistry()
    registry.register(worker)

    engine = CoordinationEngine(
        StaticCoordinator(
            [
                DelegationRequest(
                    worker_name="account",
                    task="task",
                )
            ]
        ),
        registry,
    )

    state = make_state("unused")

    engine.run(state)

    assert state.context[
        "worker_results"
    ] == [
        {
            "worker_name": "account",
            "output": {
                "value": 42,
            },
        }
    ]


def test_unknown_worker_fails_safely() -> None:
    registry = WorkerRegistry()

    coordinator = StaticCoordinator(
        [
            DelegationRequest(
                worker_name="missing",
                task="task",
            )
        ]
    )

    engine = CoordinationEngine(
        coordinator,
        registry,
    )

    with pytest.raises(
        WorkerNotFoundError,
        match="not registered",
    ):
        engine.run(
            make_state("unused")
        )


def test_worker_cannot_claim_another_worker_result() -> None:
    class InvalidWorker:
        @property
        def name(self) -> str:
            return "account"

        def run(
            self,
            task: str,
            state: WorkflowState,
        ) -> WorkerResult:
            return WorkerResult(
                worker_name="transaction",
                output="invalid",
            )

    registry = WorkerRegistry()
    registry.register(
        InvalidWorker()
    )

    coordinator = StaticCoordinator(
        [
            DelegationRequest(
                worker_name="account",
                task="task",
            )
        ]
    )

    engine = CoordinationEngine(
        coordinator,
        registry,
    )

    with pytest.raises(
        ValueError,
        match="different worker name",
    ):
        engine.run(
            make_state("unused")
        )


def test_worker_registry_rejects_duplicate_workers() -> None:
    registry = WorkerRegistry()

    registry.register(
        RecordingWorker(
            "account",
            "first",
        )
    )

    with pytest.raises(
        WorkerAlreadyRegisteredError,
        match="already registered",
    ):
        registry.register(
            RecordingWorker(
                "account",
                "second",
            )
        )


def test_worker_registry_returns_registered_worker() -> None:
    worker = RecordingWorker(
        "account",
        "result",
    )

    registry = WorkerRegistry()
    registry.register(worker)

    assert registry.get(
        "account"
    ) is worker


def test_trace_records_delegation() -> None:
    worker = RecordingWorker(
        "account",
        "result",
    )

    registry = WorkerRegistry()
    registry.register(worker)

    engine = CoordinationEngine(
        StaticCoordinator(
            [
                DelegationRequest(
                    worker_name="account",
                    task="Get ACC001",
                )
            ]
        ),
        registry,
    )

    engine.run(
        make_state("unused")
    )

    delegation_events = [
        event
        for event in engine.trace
        if event.event_type
        is CoordinationTraceEventType
        .DELEGATION_SELECTED
    ]

    assert len(
        delegation_events
    ) == 1

    assert (
        delegation_events[0]
        .worker_name
        == "account"
    )

    assert (
        delegation_events[0].task
        == "Get ACC001"
    )


def test_trace_records_worker_execution() -> None:
    worker = RecordingWorker(
        "account",
        "result",
    )

    registry = WorkerRegistry()
    registry.register(worker)

    engine = CoordinationEngine(
        StaticCoordinator(
            [
                DelegationRequest(
                    worker_name="account",
                    task="task",
                )
            ]
        ),
        registry,
    )

    engine.run(
        make_state("unused")
    )

    event_types = [
        event.event_type
        for event in engine.trace
    ]

    assert (
        CoordinationTraceEventType
        .WORKER_STARTED
        in event_types
    )

    assert (
        CoordinationTraceEventType
        .WORKER_COMPLETED
        in event_types
    )


def test_trace_is_reset_between_runs() -> None:
    worker = RecordingWorker(
        "account",
        "result",
    )

    registry = WorkerRegistry()
    registry.register(worker)

    engine = CoordinationEngine(
        StaticCoordinator(
            [
                DelegationRequest(
                    worker_name="account",
                    task="task",
                )
            ]
        ),
        registry,
    )

    engine.run(
        make_state("first")
    )

    first_trace_length = len(
        engine.trace
    )

    engine.run(
        make_state("second")
    )

    second_trace_length = len(
        engine.trace
    )

    assert (
        second_trace_length
        == first_trace_length
    )