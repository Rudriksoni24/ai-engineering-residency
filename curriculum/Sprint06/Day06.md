# Sprint 6 — Day 6: Failure Recovery and Retry

## Artifact

Resilient Workflow Engine

## Learning Objectives

By the end of this day I should understand:

- why retry is a policy rather than a generic exception loop
- the difference between recoverable and terminal failures
- how maximum-attempt limits prevent infinite retry loops
- how retry metadata can be stored in serializable workflow state
- why workflow recovery should remain compatible with checkpoint persistence
- why retry and approval are separate concerns
- why sleepers should be injected for deterministic testing
- how retry trace events improve observability
- why idempotency matters when retrying side effects
- why persistence alone does not guarantee exactly-once execution

## Failure Categories

A recoverable failure is a failure that may succeed if the operation is tried
again.

Examples:

- temporary service unavailability
- connection reset
- rate limit
- temporary database contention

A terminal failure should not automatically be retried.

Examples:

- invalid account ID
- malformed request
- authorization denied
- unsupported action
- business-rule violation

## Retry Policy

Retry behavior should be explicit.

A policy may define:

- maximum attempts
- delay between attempts
- backoff strategy

The workflow engine should not use an unbounded while-loop.

## Attempt Semantics

For this implementation:

attempt 1 = initial execution

If max_attempts = 3:

attempt 1 -> initial try
attempt 2 -> first retry
attempt 3 -> second retry

After attempt 3 fails, the retry budget is exhausted.

## Retry State

Retry metadata should remain serializable.

Example:

state.context["retry"] = {
    "node": "transaction_worker",
    "attempt": 2,
    "max_attempts": 3,
    "last_error": "temporary unavailable",
    "status": "retrying"
}

## Persistence

After a failed recoverable attempt, the workflow checkpoint should still point
to the node that has not completed successfully.

This allows a later process to retry that node.

## Observability

Operational retry trace may include:

- attempt started
- attempt failed
- retry scheduled
- node recovered
- retry exhausted
- terminal failure

Do not store hidden model reasoning.

## Idempotency

A retry may execute a node more than once.

Therefore side-effecting operations should ideally support:

- idempotency keys
- deduplication
- transactional writes
- operation IDs

Retry does not provide exactly-once execution.

## Day 6 Boundary

Today implements:

- retry policy
- recoverable failure type
- terminal failure handling
- attempt tracking
- retry metadata
- retry trace events
- bounded retries
- injected sleeper
- persistent checkpoint compatibility

Today does NOT implement:

- distributed retry queues
- circuit breakers
- dead-letter queues
- exponential jitter
- exactly-once execution
- Sprint 6 final integration