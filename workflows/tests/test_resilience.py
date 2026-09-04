from pathlib import Path

import pytest

from workflows.contracts.state import (
    WorkflowState,
)
from workflows.graph.engine import (
    END,
    WorkflowGraph,
)
from workflows.persistence.sqlite_store import (
    SQLiteCheckpointStore,
)
from workflows.resilience.contracts import (
    RecoverableWorkflowError,
    RetryExhaustedError,
    RetryTraceEventType,
)
from workflows.resilience.engine import (
    ResilientWorkflowEngine,
)
from workflows.resilience.policy import (
    RetryPolicy,
)


def make_store(
    tmp_path: Path,
) -> SQLiteCheckpointStore:
    return SQLiteCheckpointStore(
        tmp_path / "workflow.db"
    )


def make_state() -> WorkflowState:
    return WorkflowState.create(
        {
            "request": "run task",
        },
        workflow_id="workflow-001",
    )


def build_single_node_graph(
    handler,
) -> WorkflowGraph:
    graph = WorkflowGraph()

    graph.add_node(
        "worker",
        handler,
    )

    graph.set_start(
        "worker"
    )

    graph.add_edge(
        "worker",
        END,
    )

    return graph


def test_retry_policy_requires_positive_attempts() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        RetryPolicy(
            max_attempts=0
        )


def test_retry_policy_rejects_negative_delay() -> None:
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        RetryPolicy(
            delay_seconds=-1
        )


def test_successful_node_executes_once(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(1)
        state.result = "ok"
        return state

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=3,
        ),
        sleeper=lambda _: None,
    )

    result = engine.start(
        make_state()
    )

    assert result.result == "ok"
    assert len(calls) == 1


def test_recoverable_failure_is_retried(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(1)

        if len(calls) == 1:
            raise (
                RecoverableWorkflowError(
                    "temporary failure"
                )
            )

        state.result = "recovered"

        return state

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=3,
        ),
        sleeper=lambda _: None,
    )

    result = engine.start(
        make_state()
    )

    assert result.result == "recovered"
    assert len(calls) == 2


def test_recoverable_failure_can_recover_on_final_attempt(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(1)

        if len(calls) < 3:
            raise (
                RecoverableWorkflowError(
                    "temporary"
                )
            )

        state.result = "ok"

        return state

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=3,
        ),
        sleeper=lambda _: None,
    )

    result = engine.start(
        make_state()
    )

    assert result.result == "ok"
    assert len(calls) == 3


def test_retry_exhaustion_raises_predictably(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(1)

        raise (
            RecoverableWorkflowError(
                "still unavailable"
            )
        )

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=3,
        ),
        sleeper=lambda _: None,
    )

    with pytest.raises(
        RetryExhaustedError,
        match="3 attempts",
    ):
        engine.start(
            make_state()
        )

    assert len(calls) == 3


def test_terminal_failure_is_not_retried(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(1)

        raise ValueError(
            "invalid request"
        )

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=5,
        ),
        sleeper=lambda _: None,
    )

    with pytest.raises(
        ValueError,
        match="invalid request",
    ):
        engine.start(
            make_state()
        )

    assert len(calls) == 1


def test_retry_uses_injected_sleeper(
    tmp_path: Path,
) -> None:
    calls: list[int] = []
    sleeps: list[float] = []

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(1)

        if len(calls) == 1:
            raise (
                RecoverableWorkflowError(
                    "temporary"
                )
            )

        return state

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=2,
            delay_seconds=1.5,
        ),
        sleeper=sleeps.append,
    )

    engine.start(
        make_state()
    )

    assert sleeps == [
        1.5,
    ]


def test_retry_metadata_is_persisted_when_exhausted(
    tmp_path: Path,
) -> None:
    store = make_store(
        tmp_path
    )

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        raise (
            RecoverableWorkflowError(
                "service unavailable"
            )
        )

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        store,
        retry_policy=RetryPolicy(
            max_attempts=2,
        ),
        sleeper=lambda _: None,
    )

    state = make_state()

    with pytest.raises(
        RetryExhaustedError
    ):
        engine.start(state)

    checkpoint = store.load(
        state.workflow_id
    )

    assert checkpoint is not None

    assert (
        checkpoint.next_node
        == "worker"
    )

    assert checkpoint.completed is False

    retry = (
        checkpoint.state.context[
            "retry"
        ]
    )

    assert retry[
        "status"
    ] == "exhausted"

    assert retry[
        "attempt"
    ] == 2

    assert retry[
        "max_attempts"
    ] == 2


def test_terminal_failure_metadata_is_persisted(
    tmp_path: Path,
) -> None:
    store = make_store(
        tmp_path
    )

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        raise ValueError(
            "bad input"
        )

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        store,
        retry_policy=RetryPolicy(
            max_attempts=3,
        ),
        sleeper=lambda _: None,
    )

    state = make_state()

    with pytest.raises(
        ValueError
    ):
        engine.start(state)

    checkpoint = store.load(
        state.workflow_id
    )

    assert checkpoint is not None

    retry = (
        checkpoint.state.context[
            "retry"
        ]
    )

    assert (
        retry["status"]
        == "terminal_failure"
    )

    assert retry[
        "attempt"
    ] == 1


def test_retry_state_is_removed_after_success(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(1)

        if len(calls) == 1:
            raise (
                RecoverableWorkflowError(
                    "temporary"
                )
            )

        state.result = "ok"
        return state

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=2,
        ),
        sleeper=lambda _: None,
    )

    result = engine.start(
        make_state()
    )

    assert (
        "retry"
        not in result.context
    )


def test_trace_records_attempt_failure_and_recovery(
    tmp_path: Path,
) -> None:
    calls: list[int] = []

    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        calls.append(1)

        if len(calls) == 1:
            raise (
                RecoverableWorkflowError(
                    "temporary"
                )
            )

        return state

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=2,
        ),
        sleeper=lambda _: None,
    )

    engine.start(
        make_state()
    )

    event_types = [
        event.event_type
        for event in engine.trace
    ]

    assert (
        RetryTraceEventType
        .ATTEMPT_FAILED
        in event_types
    )

    assert (
        RetryTraceEventType
        .RETRY_SCHEDULED
        in event_types
    )

    assert (
        RetryTraceEventType
        .NODE_RECOVERED
        in event_types
    )

    assert (
        RetryTraceEventType
        .NODE_COMPLETED
        in event_types
    )


def test_trace_records_retry_exhaustion(
    tmp_path: Path,
) -> None:
    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        raise (
            RecoverableWorkflowError(
                "temporary"
            )
        )

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        retry_policy=RetryPolicy(
            max_attempts=2,
        ),
        sleeper=lambda _: None,
    )

    with pytest.raises(
        RetryExhaustedError
    ):
        engine.start(
            make_state()
        )

    assert (
        RetryTraceEventType
        .RETRY_EXHAUSTED
        in [
            event.event_type
            for event in engine.trace
        ]
    )


def test_trace_records_terminal_failure(
    tmp_path: Path,
) -> None:
    def worker(
        state: WorkflowState,
    ) -> WorkflowState:
        raise ValueError(
            "permanent"
        )

    engine = ResilientWorkflowEngine(
        build_single_node_graph(
            worker
        ),
        make_store(tmp_path),
        sleeper=lambda _: None,
    )

    with pytest.raises(
        ValueError
    ):
        engine.start(
            make_state()
        )

    assert (
        RetryTraceEventType
        .TERMINAL_FAILURE
        in [
            event.event_type
            for event in engine.trace
        ]
    )

def test_failed_node_can_resume_with_new_engine(
        tmp_path: Path,
    ) -> None:
        database_path = (
            tmp_path / "workflow.db"
        )

        first_calls: list[int] = []

        def failing_worker(
            state: WorkflowState,
        ) -> WorkflowState:
            first_calls.append(1)

            raise (
                RecoverableWorkflowError(
                    "temporary outage"
                )
            )

        first_store = (
            SQLiteCheckpointStore(
                database_path
            )
        )

        first_engine = (
            ResilientWorkflowEngine(
                build_single_node_graph(
                    failing_worker
                ),
                first_store,
                retry_policy=RetryPolicy(
                    max_attempts=1,
                ),
                sleeper=lambda _: None,
            )
        )

        state = make_state()

        with pytest.raises(
            RetryExhaustedError
        ):
            first_engine.start(state)

        assert first_calls == [1]

        second_calls: list[int] = []

        def recovered_worker(
            state: WorkflowState,
        ) -> WorkflowState:
            second_calls.append(1)

            state.result = "recovered"

            return state

        second_store = (
            SQLiteCheckpointStore(
                database_path
            )
        )

        second_engine = (
            ResilientWorkflowEngine(
                build_single_node_graph(
                    recovered_worker
                ),
                second_store,
                retry_policy=RetryPolicy(
                    max_attempts=2,
                ),
                sleeper=lambda _: None,
            )
        )

        result = second_engine.resume(
            state.workflow_id
        )

        assert (
            result.result
            == "recovered"
        )

        assert second_calls == [1]