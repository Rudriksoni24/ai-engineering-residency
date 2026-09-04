# Sprint 6 — Day 3 Report

## Title

Persistence and Checkpointing

## Artifact

Persistent Agent State

## Objective

Make workflow execution durable across process interruption.

## Implemented

- WorkflowCheckpoint contract
- CheckpointStore abstraction
- SQLiteCheckpointStore
- workflow state serialization
- workflow state deserialization
- persistent workflow IDs
- durable graph execution position
- checkpoint save
- checkpoint load
- workflow resume
- completed workflow loading
- safe missing-workflow handling
- deterministic interruption simulation
- persistence regression tests

## Persistent Architecture

Workflow
  ↓
Node Execution
  ↓
Updated State
  ↓
Routing Decision
  ↓
Checkpoint
  ↓
SQLite

Process may terminate.

New process:

SQLite
  ↓
Load Checkpoint
  ↓
Restore WorkflowState
  ↓
Restore next node
  ↓
Resume execution

## Checkpoint Invariant

The checkpoint's next_node represents the next workflow node that has not yet
executed.

This reduces ambiguity during resume.

## Serialization

Workflow state is explicitly converted to and from serializable dictionaries.

Persisted data includes:

- workflow ID
- workflow status
- input
- context
- result
- error
- transition history

Runtime infrastructure is not persisted.

## Persistence Abstraction

The workflow engine depends on CheckpointStore rather than SQLite directly.

SQLiteCheckpointStore provides today's deterministic local implementation.

## Completed Workflow Behavior

Completed workflows remain loadable.

Resuming an already completed workflow returns its persisted final state without
executing nodes again.

## Missing Workflow Behavior

Checkpoint storage returns no result for an unknown workflow ID.

Resume converts that into a clear WorkflowCheckpointNotFoundError.

## Limitations

The current store maintains only the latest checkpoint per workflow.

The implementation does not yet solve crashes occurring after a node side
effect but before checkpoint persistence.

Idempotency, transactional side effects, retry semantics, and failure recovery
are deferred.

## Validation

uv run pytest workflows/tests/test_persistence.py -v
uv run pytest workflows/tests -v
uv run pytest agents/tests -v
uv run pytest -v

If configured:

uv run ruff check workflows agents

## Result

Sprint 6 Day 3 proves that workflow state survives process boundaries and that
execution can resume from durable graph position using a new engine instance.