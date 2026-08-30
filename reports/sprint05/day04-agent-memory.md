# Sprint 5 — Day 4 Report
## Memory Fundamentals

### Artifact

Agent Memory Layer

---

## Objective

Extend the iterative ReAct-style agent with bounded conversational memory
without breaking the existing stateless agent architecture.

---

## What I Built

Implemented:

- MemoryMessage contract
- AgentMemory bounded message store
- user/assistant conversational memory
- configurable maximum memory size
- immutable memory snapshots
- memory clearing
- prompt-level memory injection
- optional memory support in ReActAgent
- successful-turn memory commits
- failure-safe memory behavior
- multi-turn deterministic tests
- local Ollama memory demonstration

---

## Architecture

The application owns memory.

The model receives memory only when the prompt builder injects previously
completed conversation turns into the current prompt.

Current-run tool observations remain part of the AgentStep trajectory.

Previous completed conversations belong to AgentMemory.

---

## Memory Lifecycle

Before run:

read previous completed memory

During run:

use stable memory snapshot
execute ReAct tool loop
record current observations as AgentStep objects

After successful final answer:

commit user query
commit assistant answer

After failed run:

do not commit the turn

---

## Important Concepts

LLM context and agent memory are not the same concept.

Context is the information visible during one generation.

Memory is application-managed information retained between generations.

The application controls which memory is stored and which memory is
reintroduced into model context.

---

## Bounded Memory

Memory uses a bounded deque.

When the configured message limit is exceeded, oldest messages are removed.

This prevents unlimited conversation-history growth.

The current implementation is message-count based rather than token-count
based.

---

## Design Decisions

Memory remains optional so existing Day 3 ReActAgent users can continue
running without state.

The existing ReAct execution loop was extended rather than duplicated.

Raw tool observations are not persisted as general conversational memory.

Only completed user/assistant turns are committed.

Failed executions do not automatically modify conversational memory.

---

## Testing

Added tests covering:

- message storage
- bounded eviction
- invalid memory configuration
- empty memory content rejection
- clearing memory
- prompt memory injection
- successful memory commits
- cross-turn memory visibility
- current-turn isolation
- failed-run rollback behavior
- backward compatibility with stateless agents

---

## Limitations

The memory layer currently has:

- no persistence across processes
- no semantic retrieval
- no embeddings
- no summarization
- no token-aware context budgeting
- no database
- no automatic fact extraction
- no cross-session memory
- no multi-agent shared state

These are intentionally outside Day 4 scope.

---

## Key Takeaway

The model does not inherently remember previous API calls.

A stateful agent requires application-owned memory plus explicit context
injection.

Memory is therefore an engineering subsystem, not a magical property of
the LLM.