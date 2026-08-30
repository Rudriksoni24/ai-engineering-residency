# Sprint 5 — Day 2: Tool Design & Execution

## Objective

Build a reliable tool-management layer that allows an agent to discover, validate, and execute application capabilities through a centralized registry.

## Artifact

Agent Tool Registry

## Why Tool Design Matters

An agent is only as reliable as the tools it can invoke.

A language model may request actions using arbitrary text, but application code must convert those requests into controlled operations.

The desired execution boundary is:

```text id="s1d2-curriculum-1"
LLM
 ↓
Tool Request
 ↓
Tool Registry
 ↓
Known Tool?
 ↓
Argument Validation
 ↓
Execution
 ↓
Tool Result
```

## Tool Metadata

A useful tool definition includes:

* Name
* Description
* Argument schema
* Execution implementation

For example:

```text id="s1d2-curriculum-2"
Tool:
get_account

Description:
Retrieve banking account information.

Arguments:
account_id: string, required
```

The model should receive the metadata but not direct access to implementation objects.

## Tool Registry

A tool registry provides a central catalog of available tools.

Responsibilities include:

* Register tools
* Reject duplicate names
* Discover tools
* Retrieve tool metadata
* Resolve requested tools by name

The agent should not maintain its own ad hoc tool dictionary.

## Tool Executor

The registry answers:

```text id="s1d2-curriculum-3"
What tools exist?
```

The executor answers:

```text id="s1d2-curriculum-4"
Can this requested tool call be executed safely?
```

Separating discovery from execution keeps responsibilities clear.

## Argument Validation

A model-generated tool call is untrusted input.

Example:

```json id="s1d2-curriculum-5"
{
  "tool_name": "get_account",
  "arguments": {
    "account_id": 123
  }
}
```

If the tool requires a string account ID, this must be rejected before business logic executes.

Validation should happen at the application boundary.

## Tool Result

Tool execution should return structured status rather than forcing the agent to interpret exceptions as normal behavior.

A result can represent:

* Success
* Failure
* Tool name
* Observation
* Error message

This will become important when the Day 3 agent loop receives observations from multiple tool executions.

## Read Tools vs Write Tools

Tools can have fundamentally different risk levels.

Read-only examples:

* Get account
* Find transaction
* Search policy

Write examples:

* Freeze account
* Transfer funds
* Update customer details

A production system should not treat them identically.

Sprint 5 begins with deterministic read-only tools.

## Tool Discovery

Prompt construction should be driven by registry metadata.

The application should not maintain a separate hard-coded list of tool descriptions.

That prevents tool implementation and prompt metadata from drifting apart.

## Execution Authority

The LLM can request:

```text id="s1d2-curriculum-6"
get_account
```

but only the application can determine whether:

* The tool is registered
* The arguments are valid
* The caller is authorized
* Execution is allowed

Therefore:

```text id="s1d2-curriculum-7"
Tool request ≠ Tool permission
```

## Definition of Done

* [ ] Tool argument contracts implemented.
* [ ] Structured ToolResult implemented.
* [ ] Tool registry implemented.
* [ ] Duplicate tool registration rejected.
* [ ] Tool lookup implemented.
* [ ] Tool discovery metadata implemented.
* [ ] Centralized tool executor implemented.
* [ ] Unknown tools rejected safely.
* [ ] Invalid arguments rejected safely.
* [ ] Multiple banking tools implemented.
* [ ] MinimalAgent migrated to registry/executor.
* [ ] Prompt generated from registry metadata.
* [ ] Unit tests passing.
* [ ] Runnable Agent Tool Registry demonstrated.
* [ ] Full repository regression passing.
* [ ] Report completed.
* [ ] Scoreboard updated.
* [ ] Git changes committed and merged.
