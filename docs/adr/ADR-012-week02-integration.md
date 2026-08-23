# ADR-012: Week 2 End-to-End Integration

## Status

Accepted

## Context

Week 2 implemented multiple Transformer and language-model components
independently.

Individual components passing unit tests does not guarantee that the
complete system works correctly.

## Decision

Create an end-to-end integration pipeline that:

- Loads text
- Tokenizes text
- Creates next-token training samples
- Initializes MiniGPT
- Trains the model
- Saves a checkpoint
- Loads the checkpoint into a fresh model
- Generates text

## Consequences

### Positive

- Validates component interoperability.
- Creates a reproducible demonstration.
- Exposes integration bugs.
- Establishes an engineering baseline for future ML systems.

### Negative

- The system remains intentionally small.
- Passing integration tests does not demonstrate general language
  understanding or production readiness.