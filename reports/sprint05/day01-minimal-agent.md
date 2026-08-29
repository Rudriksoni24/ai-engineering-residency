# Sprint 5 — Day 1 Report: Minimal Tool-Using Agent

## Summary

Implemented the foundational architecture of a tool-using AI agent without relying on an agent framework.

The system allows a local language model to decide whether a user request should be answered directly or handled through an application-provided banking tool.

## Artifact

Minimal Tool-Using Agent

## Architecture

```text
User Request
     ↓
AgentPromptBuilder
     ↓
Local LLM
     ↓
Structured Decision
     ↓
AgentDecisionParser
   ┌──────┴───────┐
   ↓              ↓
 Final          Tool
   ↓              ↓
Answer      Tool Execution
                  ↓
              Observation
```

## Components

### AgentDecision

Represents the action selected by the model.

Supported decisions:

* `final`
* `tool`

### ToolCall

Contains:

* Tool name
* Tool arguments

### AgentTool

Defines the application contract for capabilities available to the agent.

### GetAccountTool

Provides deterministic banking account lookup.

### AgentPromptBuilder

Describes available tools and requires the model to return a structured JSON decision.

### AgentDecisionParser

Validates model-generated JSON and converts it into application-level decision objects.

### MinimalAgent

Coordinates:

1. Prompt construction
2. Model generation
3. Decision parsing
4. Tool validation
5. Tool execution
6. Response construction

## Security Boundary

The language model does not directly execute tools.

It requests a tool invocation.

The application verifies that the requested tool exists before execution.

Therefore:

```text
Model Request
≠
Execution Authority
```

## Current Limitation

The Day 1 implementation supports at most one tool invocation.

After a tool executes, its observation is returned directly rather than being sent back to the language model.

A later Sprint 5 day will introduce an iterative agent loop.

## Key Learning

An agent differs from a fixed RAG pipeline because the model participates in deciding what action should happen next.

However, the application remains responsible for controlling which actions are actually permitted.

## Validation

```bash
uv run pytest agents/tests -v

uv run python -m agents.scripts.run_minimal_agent

uv run pytest -v
```

## Next Step

Sprint 5 Day 2 will focus on tool design, validation, registration, discovery, and execution through an Agent Tool Registry.
