# Sprint 5 — Day 3: Reasoning & Agent Loop

## Artifact

ReAct-Style Agent

## Learning objectives

By the end of this day I should be able to:

- explain why one tool call does not make an iterative agent
- implement a decision/action/observation loop
- feed tool observations back into later model calls
- maintain an application-safe execution trajectory
- support multiple sequential tool calls
- enforce a maximum iteration limit
- distinguish model decisions from application execution
- test an agent loop without requiring a live LLM

## Mental model

A tool-using agent repeatedly alternates between model decisions and
environment observations.

User Goal
→ Model Decision
→ Tool Action
→ Tool Result
→ Observation
→ Model Decision
→ ...
→ Final Answer

The model proposes actions.

The application decides whether those actions are valid and executable.

## Action

An action is an externally visible operation proposed by the model.

For this project, an action is represented by a tool call containing:

- tool name
- arguments

The action itself is not trusted merely because the model emitted it.

It must pass through the AgentToolExecutor.

## Observation

An observation is the application-visible result of executing an action.

Examples:

- transaction details
- account details
- validation failure
- tool execution failure

Observations become input to subsequent model decisions.

## Trajectory

A trajectory is the application-safe history of actions and observations
produced while completing one task.

The trajectory stores information such as:

- iteration number
- requested tool
- arguments
- observation

It must not require or persist private model chain-of-thought.

## Iterative execution

The Day 2 MinimalAgent performs at most one tool action.

The Day 3 ReActAgent repeats:

1. build prompt
2. ask model for one decision
3. parse decision
4. return if final
5. execute tool if action
6. append observation to trajectory
7. build another prompt
8. continue

## Multi-step tool use

Example:

Question:

Who owns the account connected to transaction TXN9001?

Possible execution:

Iteration 1:
get_transaction(transaction_id="TXN9001")

Observation:
Transaction TXN9001 belongs to ACC001.

Iteration 2:
get_account(account_id="ACC001")

Observation:
ACC001 is owned by Ravi Sharma.

Iteration 3:
final answer

The tools remain independent.

get_transaction does not invoke get_account.

The agent chooses the second action after receiving the first observation.

## Maximum iterations

An agent must not be allowed to execute indefinitely.

The loop therefore has a configured max_iterations value.

If the model continues requesting tools after the limit is exhausted,
execution stops with a controlled failure.

This protects against:

- malformed model behavior
- repetitive actions
- accidental infinite loops
- unnecessary tool cost
- runaway latency

## Security boundary

LLM tool request != execution permission.

Only the application executes tools.

The AgentToolRegistry defines available tools.

The AgentToolExecutor validates and executes requests.

The ReActAgent orchestrates the loop but does not bypass either component.

## Testing strategy

Automated tests use deterministic fake generators.

Tests must not require Ollama.

The fake generator returns predefined model decisions so exact trajectories
can be asserted.

Required behaviors:

- direct final answer requires zero tool calls
- one-tool sequence works
- two-tool sequence works
- observations reach subsequent model calls
- invalid tool requests fail in a controlled way
- maximum iterations stop endless action requests
- execution trace is preserved

## Exit criterion

After tests pass:

[x] Implement an agent execution loop.