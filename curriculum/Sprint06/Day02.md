# Sprint 6 — Day 2: Workflow Graphs

## Artifact

Graph-Based Agent Workflow

## Learning Objectives

By the end of this day I should understand:

- how workflow graphs differ from workflow state machines
- what workflow nodes represent
- what workflow edges represent
- why a graph needs a defined start node
- how terminal nodes end workflow execution
- how conditional routing works
- how routing can depend on workflow state
- why graph topology should be validated before execution
- how execution traces provide workflow observability
- why deterministic routing should remain outside the LLM when possible

## State Machine vs Workflow Graph

A state machine models lifecycle state.

Example:

CREATED
  ↓
PLANNING
  ↓
EXECUTING
  ↓
COMPLETED

A workflow graph models execution flow.

Example:

START
  ↓
classify
  ├── account → account_worker
  ├── transaction → transaction_worker
  └── unsupported → fallback
                         ↓
                        END

The concepts are related but not identical.

Workflow status describes the lifecycle of the overall workflow.

The current graph node describes which execution step is currently running.

A workflow may remain EXECUTING while several graph nodes execute.

## Workflow Node

A workflow node is an executable unit.

Conceptually:

state -> node -> updated state

The node receives WorkflowState and returns WorkflowState.

Nodes should perform work.

They should not decide graph topology.

## Workflow Edge

An edge defines a possible transition from one node to another node.

An unconditional edge always chooses the same destination.

A conditional edge selects the destination based on workflow state.

## Start Node

Every executable graph needs a defined entry point.

The start node determines where graph execution begins.

## Terminal Node

A terminal node ends graph execution.

A terminal node has no outgoing routing requirement.

## Conditional Routing

Routing may depend on data stored in WorkflowState.

Example:

task_type = "account"
    -> account_worker

task_type = "transaction"
    -> transaction_worker

otherwise
    -> fallback

Routing should be deterministic when the routing rule itself is deterministic.

## Graph Validation

A workflow graph should be validated before execution.

Validation should detect structural problems such as:

- missing start node
- start node not registered
- edge source not registered
- edge destination not registered
- duplicate node names
- conflicting routing definitions

Graph validation protects execution from invalid topology.

## Execution Trace

An execution trace records operational workflow events.

Day 2 traces may include:

- node execution
- routing decision
- source node
- destination node

This is operational observability.

It is not hidden model chain-of-thought.

## Day 2 Boundary

Today implements:

- workflow nodes
- workflow edges
- start node
- terminal nodes
- conditional routing
- graph validation
- graph execution
- routing based on workflow state
- execution trace

Today does NOT implement:

- durable persistence
- checkpoint recovery
- coordinator agents
- independent worker agents
- human approval
- retry policies