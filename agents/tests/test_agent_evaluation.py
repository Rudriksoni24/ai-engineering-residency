from agents.contracts.agent import (
    AgentResponse,
    AgentStep,
)
from agents.evaluation.contracts import (
    AgentEvaluationCase,
)
from agents.evaluation.harness import (
    AgentEvaluationHarness,
)


class FakeAgent:
    def __init__(
        self,
        *,
        response: AgentResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error

    def run(
        self,
        user_query: str,
    ) -> AgentResponse:
        if self.error is not None:
            raise self.error

        if self.response is None:
            raise RuntimeError(
                "fake agent has no response"
            )

        return self.response


def test_successful_case_passes():
    response = AgentResponse(
        answer=(
            "Ravi Sharma owns account ACC001."
        ),
        tool_used="get_account",
        observation=(
            "Account ACC001: "
            "owner=Ravi Sharma"
        ),
        steps=(
            AgentStep(
                iteration=1,
                tool_name=(
                    "get_transaction"
                ),
                arguments={
                    "transaction_id": (
                        "TXN9001"
                    )
                },
                observation=(
                    "Transaction TXN9001: "
                    "account_id=ACC001"
                ),
            ),
            AgentStep(
                iteration=2,
                tool_name="get_account",
                arguments={
                    "account_id": (
                        "ACC001"
                    )
                },
                observation=(
                    "Account ACC001: "
                    "owner=Ravi Sharma"
                ),
            ),
        ),
    )

    agent = FakeAgent(
        response=response
    )

    case = AgentEvaluationCase(
        case_id="owner-001",
        user_query=(
            "Who owns the account "
            "associated with TXN9001?"
        ),
        required_answer_keywords=(
            "Ravi Sharma",
            "ACC001",
        ),
        expected_tools=(
            "get_transaction",
            "get_account",
        ),
        expected_tool_sequence=(
            "get_transaction",
            "get_account",
        ),
        max_steps=2,
    )

    result = (
        AgentEvaluationHarness()
        .evaluate(
            agent=agent,
            case=case,
        )
    )

    assert result.passed is True
    assert result.error is None
    assert result.step_count == 2

    assert result.actual_tools == (
        "get_transaction",
        "get_account",
    )


def test_missing_answer_keyword_fails():
    response = AgentResponse(
        answer=(
            "The account ID is ACC001."
        ),
        tool_used=(
            "get_transaction"
        ),
        observation=(
            "Transaction TXN9001: "
            "account_id=ACC001"
        ),
        steps=(
            AgentStep(
                iteration=1,
                tool_name=(
                    "get_transaction"
                ),
                arguments={
                    "transaction_id": (
                        "TXN9001"
                    )
                },
                observation=(
                    "Transaction TXN9001: "
                    "account_id=ACC001"
                ),
            ),
        ),
    )

    agent = FakeAgent(
        response=response
    )

    case = AgentEvaluationCase(
        case_id="owner-002",
        user_query=(
            "Who owns the account?"
        ),
        required_answer_keywords=(
            "Ravi Sharma",
        ),
    )

    result = (
        AgentEvaluationHarness()
        .evaluate(
            agent=agent,
            case=case,
        )
    )

    assert result.passed is False

    checks = dict(
        result.checks
    )

    assert (
        checks[
            "required_answer_keywords"
        ]
        is False
    )


def test_wrong_tool_sequence_fails():
    response = AgentResponse(
        answer=(
            "Ravi Sharma owns ACC001."
        ),
        tool_used="get_account",
        observation=(
            "Account ACC001: "
            "owner=Ravi Sharma"
        ),
        steps=(
            AgentStep(
                iteration=1,
                tool_name="get_account",
                arguments={
                    "account_id": (
                        "TAS9001"
                    )
                },
                observation=(
                    "Account TAS9001 "
                    "was not found."
                ),
            ),
            AgentStep(
                iteration=2,
                tool_name=(
                    "get_transaction"
                ),
                arguments={
                    "transaction_id": (
                        "TXN9001"
                    )
                },
                observation=(
                    "Transaction TXN9001: "
                    "account_id=ACC001"
                ),
            ),
            AgentStep(
                iteration=3,
                tool_name="get_account",
                arguments={
                    "account_id": (
                        "ACC001"
                    )
                },
                observation=(
                    "Account ACC001: "
                    "owner=Ravi Sharma"
                ),
            ),
        ),
    )

    case = AgentEvaluationCase(
        case_id="trajectory-001",
        user_query=(
            "Who owns the account "
            "associated with TXN9001?"
        ),
        required_answer_keywords=(
            "Ravi Sharma",
        ),
        expected_tool_sequence=(
            "get_transaction",
            "get_account",
        ),
    )

    result = (
        AgentEvaluationHarness()
        .evaluate(
            agent=FakeAgent(
                response=response
            ),
            case=case,
        )
    )

    assert result.passed is False

    checks = dict(
        result.checks
    )

    assert (
        checks[
            "expected_tool_sequence"
        ]
        is False
    )


def test_step_budget_is_enforced():
    response = AgentResponse(
        answer="Done.",
        tool_used="get_account",
        observation="Done.",
        steps=(
            AgentStep(
                iteration=1,
                tool_name="get_account",
                arguments={},
                observation="one",
            ),
            AgentStep(
                iteration=2,
                tool_name="get_account",
                arguments={},
                observation="two",
            ),
            AgentStep(
                iteration=3,
                tool_name="get_account",
                arguments={},
                observation="three",
            ),
        ),
    )

    case = AgentEvaluationCase(
        case_id="steps-001",
        user_query="Do the task.",
        max_steps=2,
    )

    result = (
        AgentEvaluationHarness()
        .evaluate(
            agent=FakeAgent(
                response=response
            ),
            case=case,
        )
    )

    assert result.passed is False

    checks = dict(
        result.checks
    )

    assert (
        checks["max_steps"]
        is False
    )


def test_expected_failure_can_pass():
    case = AgentEvaluationCase(
        case_id="failure-001",
        user_query=(
            "Use blocked tool."
        ),
        expected_success=False,
        expected_error_keywords=(
            "blocked",
            "get_account",
        ),
    )

    agent = FakeAgent(
        error=RuntimeError(
            "tool 'get_account' "
            "is blocked by policy"
        )
    )

    result = (
        AgentEvaluationHarness()
        .evaluate(
            agent=agent,
            case=case,
        )
    )

    assert result.passed is True
    assert result.answer is None

    assert (
        "blocked"
        in result.error
    )


def test_unexpected_failure_fails():
    case = AgentEvaluationCase(
        case_id="failure-002",
        user_query=(
            "Who owns ACC001?"
        ),
        expected_success=True,
    )

    agent = FakeAgent(
        error=RuntimeError(
            "unexpected failure"
        )
    )

    result = (
        AgentEvaluationHarness()
        .evaluate(
            agent=agent,
            case=case,
        )
    )

    assert result.passed is False


def test_evaluate_many_returns_all_results():
    harness = (
        AgentEvaluationHarness()
    )

    agent = FakeAgent(
        response=AgentResponse(
            answer="Hello",
            tool_used=None,
            observation=None,
            steps=(),
        )
    )

    cases = (
        AgentEvaluationCase(
            case_id="case-1",
            user_query="Hello",
            required_answer_keywords=(
                "Hello",
            ),
        ),
        AgentEvaluationCase(
            case_id="case-2",
            user_query="Hello again",
            required_answer_keywords=(
                "Hello",
            ),
        ),
    )

    results = harness.evaluate_many(
        agent=agent,
        cases=cases,
    )

    assert len(results) == 2

    assert all(
        result.passed
        for result in results
    )


def test_invalid_case_configuration_rejected():
    try:
        AgentEvaluationCase(
            case_id="",
            user_query="Hello",
        )
    except ValueError as exc:
        assert "case_id" in str(exc)
    else:
        raise AssertionError(
            "expected ValueError"
        )

    try:
        AgentEvaluationCase(
            case_id="x",
            user_query="",
        )
    except ValueError as exc:
        assert "user_query" in str(
            exc
        )
    else:
        raise AssertionError(
            "expected ValueError"
        )

    try:
        AgentEvaluationCase(
            case_id="x",
            user_query="Hello",
            max_steps=-1,
        )
    except ValueError as exc:
        assert "max_steps" in str(
            exc
        )
    else:
        raise AssertionError(
            "expected ValueError"
        )