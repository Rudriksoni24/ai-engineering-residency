# ADR-006: Self-Attention Implementation

## Status

Accepted

## Context

Transformer models require a mechanism for dynamically determining how
tokens influence one another.

The implementation must also support causal masking for autoregressive
language modeling.

## Decision

Use scaled dot-product attention:

Attention(Q, K, V) = softmax(QKᵀ / √dₖ)V

The implementation will support an optional causal mask.

## Consequences

### Positive

- Provides direct understanding of Q, K, and V.
- Creates a reusable attention implementation.
- Supports future autoregressive language-model experiments.

### Negative

- The implementation is educational rather than production optimized.
- Multi-head attention is deferred to Week 2 Day 2.