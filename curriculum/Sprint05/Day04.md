# Sprint 5 — Day 4
## Memory Fundamentals

### Artifact

Agent Memory Layer

---

## Learning Objectives

By the end of this day I should be able to explain:

- why LLM APIs are stateless
- the difference between model context and application memory
- short-term conversational memory
- bounded memory windows
- why memory must be explicitly injected into prompts
- why agent memory should be owned by the application
- when memory should be committed
- why failed agent runs should not automatically become trusted memory
- the difference between current-run observations and previous-turn memory
- limitations of naive conversational memory

---

## Core Mental Model

An LLM request is normally stateless.

The model receives:

prompt → generates output

On the next request, previous information is unavailable unless the
application sends it again.

Therefore:

LLM memory is usually not model memory.

It is application-managed state.

---

## Context vs Memory

Context is what the model sees during the current generation.

Memory is information retained by the application between generations.

Memory becomes useful to the model only when selected memory is inserted
back into the next prompt.

---

## Short-Term Conversation Memory

For this sprint we implement bounded short-term memory.

Example:

Turn 1:

User:
Look up account ACC001.

Assistant:
ACC001 belongs to Ravi Sharma.

Stored memory:

[
    user: Look up account ACC001.
    assistant: ACC001 belongs to Ravi Sharma.
]

Turn 2:

User:
What is the balance of that same account?

Prompt contains both the previous completed turn and the new query.

The model can therefore resolve "that same account".

---

## Memory Ownership

The application owns memory.

The LLM must not be allowed to directly mutate arbitrary application state.

The application decides:

1. what gets stored
2. when it gets stored
3. how much history is retained
4. what gets sent back to the model

---

## Memory Commit Boundary

A user message should not automatically become trusted completed history
before the agent finishes successfully.

Day 4 uses a simple transactional rule:

agent run succeeds
→ commit user message
→ commit assistant answer

agent run fails
→ do not commit that failed turn

This prevents incomplete or failed interactions from automatically becoming
normal conversation history.

---

## Bounded Memory

Conversation history grows indefinitely unless constrained.

We therefore retain only a maximum number of messages.

When the limit is exceeded, the oldest messages are removed.

This prevents unbounded context growth but introduces information loss.

---

## Current Observations vs Persistent Memory

Tool observations generated during one ReAct execution belong to the current
execution trajectory.

They are already represented by AgentStep.

We do not persist every raw tool observation into conversation memory today.

Instead, after a successful run, we persist:

user message
assistant final answer

This avoids blindly carrying potentially stale operational data into future
turns.

---

## Not Implemented Today

We deliberately do not implement:

- vector memory
- semantic memory retrieval
- long-term persistent storage
- user profile memory
- memory summarization
- embeddings
- cross-session storage
- Redis/PostgreSQL memory
- automatic fact extraction
- multi-agent shared memory

Those require additional policies and architecture.

---

## Exit Criteria

I can explain:

- why an LLM does not inherently remember previous requests
- context vs memory
- how bounded memory works
- why application code owns memory
- why memory is committed after successful execution
- why all tool observations should not automatically become persistent memory

I can implement:

- immutable memory messages
- bounded conversational memory
- prompt memory injection
- stateful multi-turn ReAct execution
- memory regression tests