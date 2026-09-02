# Sprint 6 — Day 2 Report

## Title

Workflow Graphs

## Artifact

Graph-Based Agent Workflow

## Objective

Extend the explicit workflow state foundation from Day 1 with graph-based
execution and conditional routing.

## Implemented

- workflow nodes
- unconditional workflow edges
- conditional workflow edges
- start node
- terminal END marker
- graph validation
- graph execution engine
- state-based routing
- fallback routing
- execution step protection
- execution trace
- deterministic graph tests
- runnable banking-style graph demo

## Example Graph

START
  ↓
classify
  ├── account → account_worker → END
  ├── transaction → transaction_worker → END
  └── unsupported → fallback → END

## State Machine vs Graph

Workflow state machine:

controls workflow lifecycle transitions.

Workflow graph:

controls execution-step routing.

A workflow may remain in the EXECUTING lifecycle state while multiple graph
nodes execute.

## Conditional Routing

The classification node updates workflow context.

The router reads that context and returns a semantic route key.

The graph maps that route key to a registered destination node.

This keeps state interpretation and graph topology separate.

## Validation

Graph validation detects:

- missing start node
- unregistered start node
- unregistered edge source
- unregistered edge destination
- duplicate nodes
- conflicting outgoing routing

Invalid graph topology is rejected before execution.

## Execution Trace

Operational trace events include:

- node started
- node completed
- route selected
- workflow completed

No hidden chain-of-thought is recorded.

## Safety

The graph engine has a maximum execution-step limit to protect against
unbounded cycles.

Cycles themselves are not prohibited because future retry workflows may
legitimately require them.

## Intentionally Deferred

Not implemented today:

- durable checkpoint persistence
- process restart recovery
- workflow resume
- coordinator agent
- independent worker agents
- human approval
- retry policy
- failure recovery

## Validation Commands

uv run pytest workflows/tests -v
uv run pytest agents/tests -v
uv run pytest -v

If configured:

uv run ruff check workflows agents

## Result

Sprint 6 Day 2 introduces explicit graph topology and deterministic conditional
routing while preserving the workflow state abstraction introduced on Day 1.