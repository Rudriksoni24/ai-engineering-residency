# ADR-008: Transformer Block Architecture

## Status

Accepted

## Context

The Transformer architecture combines self-attention with position-wise
feed-forward transformations. Residual connections and normalization
are used around these sublayers.

## Decision

Implement a Transformer block using the original Transformer
post-normalization structure:

LayerNorm(x + MultiHeadAttention(x))

followed by:

LayerNorm(x + FeedForward(x))

The feed-forward network uses:

d_model → d_ff → d_model

with ReLU activation.

## Consequences

### Positive

- Closely follows the original Transformer architecture.
- Separates token-to-token communication from position-wise transformation.
- Provides residual paths and normalization.
- Can be stacked to construct larger Transformer networks.

### Negative

- Post-normalization is not the only architecture used by modern
  Transformer models.
- The implementation is educational rather than optimized for production.