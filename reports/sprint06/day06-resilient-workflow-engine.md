# Sprint 6 — Day 6 Report

## Title

Failure Recovery and Retry

## Artifact

Resilient Workflow Engine

## Objective

Introduce bounded, observable retry behavior for recoverable workflow failures
while preserving deterministic terminal-failure semantics.

## Implemented

- RecoverableWorkflowError
- RetryExhaustedError
- RetryPolicy
- maximum attempt limits
- fixed retry delay configuration
- injected sleeper
- recoverable-failure retry
- terminal-failure handling
- retry metadata in WorkflowState.context
- checkpoint-before-attempt semantics
- checkpoint-on-failure semantics
- retry exhaustion
- persistent failed-node resume
- retry trace events
- deterministic tests

## Failure Categories

Recoverable failures may be retried.

Terminal failures are immediately propagated without retry.

The engine retries only explicit RecoverableWorkflowError failures.

## Retry Policy

RetryPolicy currently includes:

- max_attempts
- delay_seconds

max_attempts includes the initial attempt.

Example:

max_attempts = 3

means:

- attempt 1
- attempt 2
- attempt 3

## Retry Persistence

While a node has not completed successfully, the persisted checkpoint continues
to reference that node.

Retry metadata is stored in serializable workflow context.

Example fields:

- node
- attempt
- max_attempts
- status
- last_error
- last_error_type

## Recovery

A recoverable node may fail one or more times and later succeed within the retry
budget.

A later workflow-engine instance may also resume from the persisted failed node.

## Terminal Failure

Exceptions not classified as RecoverableWorkflowError are not retried.

The failure is persisted as terminal failure metadata and the original
exception is propagated.

## Retry Exhaustion

If a recoverable failure continues through max_attempts, RetryExhaustedError is
raised.

The checkpoint remains positioned at the failed node.

## Observability

Retry trace events include:

- attempt started
- attempt failed
- retry scheduled
- node recovered
- retry exhausted
- terminal failure
- node completed

No hidden model reasoning is stored.

## Testing

Tests inject a no-delay sleeper.

This keeps retry behavior deterministic and fast.

## Important Limitation

Retry does not guarantee exactly-once execution.

Side-effecting operations may require idempotency keys or deduplication.

## Intentionally Deferred

Not implemented:

- exponential backoff
- jitter
- circuit breakers
- dead-letter queues
- distributed retry queue
- exactly-once guarantees
- final Sprint 6 integration

## Validation

uv run pytest workflows/tests/test_resilience.py -v
uv run pytest workflows/tests -v
uv run pytest agents/tests -v
uv run pytest -v

If configured:

uv run ruff check workflows agents

## Result

Sprint 6 Day 6 introduces explicit recoverable and terminal failure handling,
bounded retries, durable retry metadata and deterministic recovery behavior.