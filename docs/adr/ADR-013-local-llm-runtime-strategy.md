# ADR-013: Local LLM Runtime Strategy

## Status

Accepted

## Context

The AI Engineering Residency requires all hands-on AI systems to support
local or on-premise execution.

Different inference runtimes expose different APIs, model formats,
performance characteristics, and operational trade-offs.

Coupling application code directly to one runtime would make later
migration and comparison unnecessarily difficult.

## Decision

Introduce a runtime abstraction layer.

The initial runtimes evaluated will be:

- Ollama
- llama.cpp

The application layer communicates through common request and response
contracts.

Runtime-specific implementation details remain inside adapters.

## Consequences

### Positive

- Runtime implementations can be compared.
- Applications remain less coupled to infrastructure.
- Local development can use one runtime while later deployments use
  another.
- Evaluation and benchmarking can compare implementations.

### Negative

- Adds an abstraction before multiple production runtimes exist.
- Common interfaces may need to evolve as streaming, embeddings,
  structured output, and tool calling are added.

## Decision Rule

Do not add methods to the abstraction until at least one concrete
application requirement justifies them.