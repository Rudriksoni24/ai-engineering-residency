# ADR-009: Transformer Architecture Mapping

## Status

Accepted

## Context

Individual Transformer components have been implemented across previous
labs, including self-attention, multi-head attention, feed-forward
networks, residual connections, LayerNorm, and causal masking.

Before constructing a GPT-style language model, these components must be
mapped to the original Transformer architecture.

## Decision

Study the original Transformer architecture before proceeding to MiniGPT.

Map each paper concept to the corresponding repository implementation and
identify missing components.

## Key Finding

The original Transformer is an encoder-decoder architecture.

The upcoming MiniGPT implementation will instead use a decoder-only
architecture with causal self-attention.

## Consequences

### Positive

- Reduces the risk of assembling components without architectural
  understanding.
- Creates a clear mapping between theory and implementation.
- Identifies the remaining work required for language modeling.

### Negative

- No major new neural architecture is implemented during this lab.
- Progress is measured through technical understanding and documentation.