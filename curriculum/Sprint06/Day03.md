# Sprint 6 — Day 3: Persistence and Checkpointing

## Artifact

Persistent Agent State

## Learning Objectives

By the end of this day I should understand:

- why explicit workflow state enables persistence
- what a workflow checkpoint represents
- why workflow IDs are required
- the difference between workflow state and checkpoint metadata
- how serializable workflow state is stored
- how persistence abstractions isolate storage technology
- how a workflow can resume after process interruption
- why graph execution position must become durable
- how completed workflows should behave when loaded
- how missing checkpoints should be handled safely

## Persistence

Persistence means workflow execution data survives the process that created it.

Without persistence:

Process A
  ↓
WorkflowState
  ↓
process terminates
  ↓
state is lost

With persistence:

Process A
  ↓
WorkflowState
  ↓
CheckpointStore
  ↓
Persistent Storage

Process B
  ↓
CheckpointStore
  ↓
WorkflowState restored

## Workflow ID

A workflow ID identifies one durable workflow execution.

Example:

workflow-123

The workflow ID lets the system distinguish:

workflow A
workflow B
workflow C

even if all use the same graph definition.

## Checkpoint

A checkpoint is a durable snapshot of workflow execution.

A checkpoint should contain enough data to continue execution later.

For Day 3 that includes:

- workflow ID
- serialized workflow state
- next graph node
- completion flag

The graph definition itself is runtime infrastructure and is not persisted.

## Serializable Workflow State

Persist data, not runtime objects.

Suitable:

- workflow ID
- status
- input
- context
- result
- error
- transition history

Unsuitable:

- database connections
- graph instances
- agents
- tool registries
- HTTP clients
- callables
- generators

## Checkpoint Store

The workflow engine should depend on an abstraction rather than directly on
SQLite.

Conceptually:

Workflow
   ↓
CheckpointStore
   ↓
SQLiteCheckpointStore

This allows another store implementation later without changing workflow logic.

## Resume

Resume requires more than restoring WorkflowState.

The engine must also know where execution should continue.

Therefore graph execution position becomes durable checkpoint metadata.

Example:

checkpoint:
  workflow_id = workflow-123
  next_node = transaction_worker
  state = {...}

After restart:

load checkpoint
  ↓
restore state
  ↓
start from transaction_worker

## Completed Workflow

A completed workflow should still be loadable.

However, resuming a completed workflow should not execute nodes again.

## Missing Workflow

A missing workflow ID should not cause undefined behavior.

The store should return no checkpoint, and the workflow layer should surface a
clear error when resume is requested.

## Day 3 Boundary

Today implements:

- workflow checkpoint model
- checkpoint store abstraction
- SQLite persistence
- state serialization
- checkpoint save/load
- graph position persistence
- workflow resume
- completed workflow loading
- safe missing-workflow handling

Today does NOT implement:

- multiple agents
- approval
- retry policy
- failure recovery