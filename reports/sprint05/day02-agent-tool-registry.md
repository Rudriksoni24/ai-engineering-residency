# Sprint 5 — Day 2 Report: Agent Tool Registry

## Summary

Implemented a centralized Agent Tool Registry and execution layer for reliable agent tool discovery, validation, and invocation.

The Minimal Tool-Using Agent from Day 1 was migrated away from direct tool ownership and now delegates tool management and execution to dedicated infrastructure.

## Artifact

Agent Tool Registry

## Architecture

```text id="s1d2-report-architecture"
LLM Tool Request
       ↓
MinimalAgent
       ↓
AgentToolExecutor
       ↓
AgentToolRegistry
       ↓
Registered AgentTool
       ↓
Tool Observation
```

## Components

### ToolParameter

Defines a tool argument including:

* Name
* Type
* Description
* Required status

### ToolDefinition

Defines the public metadata presented to an agent.

### ToolResult

Represents structured execution status containing:

* Tool name
* Success state
* Observation
* Error

### AgentToolRegistry

Provides:

* Tool registration
* Duplicate-name protection
* Tool lookup
* Required lookup
* Tool discovery
* Tool definitions

### AgentToolExecutor

Provides:

* Tool resolution
* Argument validation
* Unknown-argument rejection
* Tool execution
* Exception conversion into structured failures

### Banking Tools

The registry currently supports:

* `get_account`
* `get_transaction`

Both tools are deterministic and read-only.

## Single Source of Tool Metadata

Prompt construction now uses definitions directly from the Agent Tool Registry.

This prevents duplicated tool descriptions from drifting away from actual implementations.

## Validation Boundary

Model-produced arguments are treated as untrusted input.

The executor validates requested arguments before allowing business logic to execute.

Examples rejected before execution include:

* Missing required arguments
* Incorrect argument types
* Unknown arguments
* Unknown tool names

## Execution Authority

The language model can request a tool, but it cannot create new capabilities.

Only tools registered by the application are executable.

Therefore:

```text id="s1d2-report-boundary"
LLM Tool Request
       ≠
Execution Permission
```

## Tool Observation vs Execution Failure

A valid lookup that finds no account is still a successful tool execution with a negative observation.

Invalid arguments or unknown tools are execution failures.

This distinction prepares the system for iterative agent reasoning.

## Current Limitations

The tool system currently uses a small custom schema supporting primitive argument types.

It does not yet provide:

* JSON Schema
* Pydantic validation
* Nested input models
* Permission policies
* Write-tool approval
* Rate limiting
* Timeouts
* Retries
* Tool telemetry

These concerns can be introduced without changing the registry abstraction.

## Validation

```bash id="s1d2-report-validation"
uv run pytest agents/tests -v

uv run python -m agents.scripts.run_tool_registry

uv run python -m agents.scripts.run_minimal_agent

uv run pytest -v
```

## Key Learning

Reliable agents require more than exposing Python functions to a model.

Tools need explicit metadata, validation, controlled registration, and a safe execution boundary.

The language model should decide which capability it wants to use while application code retains authority over whether and how that capability executes.

## Next Step

Sprint 5 Day 3 will use the registry and structured ToolResult observations to build the first iterative ReAct-style agent loop.
