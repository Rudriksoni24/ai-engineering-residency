# Sprint 6 — Day 1: Stateful Agent Workflows

## Artifact

Workflow State Machine

## Learning Objectives

By the end of this day I should understand:

- the difference between agent scratchpad, conversation memory, and workflow state
- why workflow state should be explicit
- how workflow state transitions are modeled
- how transition rules protect workflow invariants
- how workflow execution history can be represented
- why workflow state should remain serializable
- how a deterministic state machine differs from an agent loop

## Core Mental Model

An agent answers:

"What action should I take next?"

A workflow answers:

"What state is this process currently in, what transitions are legal,
and what happened previously?"

These are related but different abstractions.

## Agent Scratchpad

An agent scratchpad represents temporary execution context used while solving
a task.

Examples:

- previous tool observations
- intermediate actions
- temporary execution context

It should not be confused with durable workflow state.

## Conversation Memory

Conversation memory represents information from previous interactions that may
help the model respond consistently.

Examples:

- previous messages
- user preferences
- conversation summaries

Conversation memory is primarily interaction context.

## Workflow State

Workflow state represents the explicit operational state of a process.

Examples:

- workflow identifier
- workflow status
- workflow input
- accumulated result
- transition history

Workflow state should be inspectable and serializable.

## State Machine

A state machine defines:

1. possible workflow states
2. legal transitions between those states
3. rules preventing illegal transitions

Example:

CREATED
  ↓
PLANNING
  ↓
EXECUTING
  ↓
COMPLETED

Failures may transition active states into FAILED.

Terminal states must not transition elsewhere.

## Why Explicit State Matters

A workflow should not hide important state inside local variables in a while
loop.

Explicit state enables later capabilities such as:

- graph routing
- persistence
- checkpointing
- workflow resume
- human approval
- retries
- multi-agent coordination
- tracing

## Determinism

Today's workflow state machine is deterministic.

Given:

- the same current status
- the same requested transition

the transition result must always be the same.

No LLM is required to decide whether a state transition is valid.

## Serializable State

Workflow state should contain data rather than runtime infrastructure.

Good workflow state:

- strings
- identifiers
- enums
- dictionaries
- lists
- results
- transition records

Bad persisted workflow state:

- database connections
- HTTP clients
- tool registries
- agent implementation instances
- lambdas
- generators

Runtime dependencies belong outside persisted state.

## Day 1 Boundary

Today implements:

- explicit workflow state
- workflow status
- transition contract
- transition validation
- state machine
- state inspection
- transition history
- invalid transition protection

Today does NOT implement:

- workflow graphs
- durable persistence
- multiple agents
- human approval
- retry policies