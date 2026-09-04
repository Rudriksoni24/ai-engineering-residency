# Sprint 6 — Day 4: Multi-Agent Coordination

## Artifact

Coordinator and Worker Agents

## Learning Objectives

By the end of this day I should understand:

- what multi-agent coordination means
- how coordinator and worker responsibilities differ
- why delegation should be explicit
- why workers should not know or control unrelated workers
- how worker registries separate discovery from execution
- how multiple workers can participate in one workflow
- how worker results are returned to workflow state
- how delegation can be traced without exposing hidden reasoning
- why deterministic fake agents are useful for orchestration tests
- how Sprint 5 agents can later be adapted into worker boundaries

## Agent vs Workflow

An agent decides or acts within a task.

A workflow coordinates execution across states, agents, branches,
checkpoints, approvals and failures.

The workflow should not disappear just because multiple agents are involved.

## Coordinator Agent

The coordinator decides which worker or workers should receive work.

The coordinator does not perform account, transaction or knowledge work itself.

Conceptually:

Workflow Request
  ↓
Coordinator
  ↓
Delegation Requests

## Worker Agent

A worker owns a specific capability.

Examples:

Account Worker
Transaction Worker
Knowledge Worker

A worker receives a delegated task and returns a result.

A worker should not directly invoke unrelated workers.

## Delegation Request

Delegation should be represented explicitly.

Example:

worker_name = account
task = "Get account ACC001"

This makes delegation testable and observable.

## Worker Registry

The worker registry maps a stable worker name to a worker implementation.

Example:

account -> AccountWorker
transaction -> TransactionWorker
knowledge -> KnowledgeWorker

The coordinator names a worker.

The registry resolves the implementation.

## Multiple Workers

One request may require multiple capabilities.

Example:

"Find account ACC001 and explain what the transaction history means."

Coordinator may delegate:

1. account worker
2. knowledge worker

The coordination engine executes each delegation and aggregates results.

## Observability

Trace operational events such as:

- coordinator started
- delegation selected
- worker started
- worker completed
- worker failed or was unavailable

Do not record hidden model reasoning.

## Day 4 Boundary

Today implements:

- coordinator contract
- worker contract
- explicit delegation request
- worker registry
- deterministic coordinator
- multiple worker delegation
- worker execution
- result aggregation
- delegation trace
- unknown worker protection

Today does NOT implement:

- human approval
- retry policy
- failure recovery
- LLM-dependent orchestration tests