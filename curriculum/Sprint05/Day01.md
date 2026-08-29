# Sprint 5 — Day 1: Agent Fundamentals & Architecture

## Objective

Understand the fundamental architecture of an AI agent and implement a minimal agent capable of deciding whether to answer directly or invoke a tool.

## Artifact

Minimal Tool-Using Agent

## LLM vs RAG vs Workflow vs Agent

### LLM

An LLM transforms input into generated output.

```text
Prompt
  ↓
LLM
  ↓
Response
```

The application decides what context and operations are available.

### RAG

A RAG system retrieves external knowledge before generation.

```text
Question
   ↓
Retrieval
   ↓
Context
   ↓
LLM
   ↓
Answer
```

The retrieval process is normally controlled by application code.

### Workflow

A workflow has predetermined control flow.

```text
Step A
 ↓
Step B
 ↓
Step C
```

Application code decides what happens next.

### Agent

An agent allows the model to participate in deciding what happens next.

```text
User Goal
    ↓
Agent
    ↓
LLM Decision
 ┌──────┴───────┐
 ↓              ↓
Tool          Answer
 ↓
Observation
 ↓
Agent
```

This decision boundary is what makes an agent fundamentally different from a fixed pipeline.

## Core Agent Components

A useful minimal agent contains:

### Model

Produces decisions or answers.

### Tools

Expose capabilities outside the language model.

Examples:

* Search account data
* Query transaction history
* Retrieve documents
* Call an API
* Perform calculations

### Tool Contract

Defines:

* Tool name
* Description
* Expected arguments
* Tool execution behavior

### Decision Parser

Converts model output into an application-level action.

### Agent

Coordinates model decisions and tool execution.

## Tool Use

A language model does not directly execute application code.

Instead:

```text
LLM
 ↓
Tool Request
 ↓
Application
 ↓
Tool Execution
 ↓
Observation
 ↓
LLM
```

The application remains responsible for execution.

This boundary is critical for security and reliability.

## Agent Decision

For Day 1 the model can produce one of two decisions:

```text
FINAL
```

or:

```text
TOOL
```

A tool decision contains:

* Tool name
* Tool arguments

A final decision contains:

* Final answer

## Structured Decisions

Free-form model text is difficult for software to execute safely.

Instead of:

```text
I think I should probably look up account ACC001.
```

we want:

```json
{
  "type": "tool",
  "tool_name": "get_account",
  "arguments": {
    "account_id": "ACC001"
  }
}
```

Structured output allows application code to validate the model's requested action.

## Tool Safety Boundary

The LLM may request a tool.

The application decides whether that tool exists and whether the arguments are valid.

Therefore:

```text
LLM request ≠ automatic execution authority
```

This becomes increasingly important when agents gain access to:

* Databases
* Email
* Payment systems
* Infrastructure
* File systems
* Production APIs

## Day 1 Limitation

Today's agent performs at most one tool call.

```text
Decision
 ↓
Tool
 ↓
Final response
```

It does not yet repeatedly reason over observations.

The multi-step agent loop will be introduced later in Sprint 5.

## Why Build This Without a Framework?

Agent frameworks are useful, but learning only a framework can hide the underlying mechanics.

Building the minimal architecture directly teaches:

* Tool contracts
* Model decisions
* Parsing
* Execution boundaries
* Observations
* Agent orchestration

Once these concepts are understood, frameworks become implementation choices rather than magic.

## Definition of Done

* [ ] Agent decision contracts implemented.
* [ ] Tool abstraction implemented.
* [ ] Banking account tool implemented.
* [ ] Agent prompt builder implemented.
* [ ] Structured decision parser implemented.
* [ ] Minimal agent implemented.
* [ ] Direct-answer path tested.
* [ ] Tool-selection path tested.
* [ ] Unknown-tool behavior tested.
* [ ] Deterministic unit tests passing.
* [ ] Local Ollama integration working.
* [ ] Runnable minimal agent demonstrated.
* [ ] Full repository regression passing.
* [ ] Report completed.
* [ ] Scoreboard updated.
* [ ] Git changes committed and merged.
