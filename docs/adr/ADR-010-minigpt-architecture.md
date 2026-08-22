# ADR-010: MiniGPT Architecture

## Status

Accepted

## Context

Previous labs implemented the major building blocks required for a
Transformer-based language model:

- Positional encoding
- Scaled dot-product attention
- Causal masking
- Multi-head attention
- Feed-forward network
- Residual connections
- Layer normalization
- Transformer block

A complete model architecture is required before training.

## Decision

Implement a small decoder-only GPT-style language model using:

- Token embeddings
- Learned positional embeddings
- Configurable Transformer blocks
- Causal self-attention
- Final LayerNorm
- Linear language model head

The architecture is intentionally small and educational.

## Consequences

### Positive

- Provides a complete end-to-end language model architecture.
- Reuses previously implemented Transformer components.
- Supports configurable model sizes.
- Prepares the repository for training and generation.

### Negative

- This is not an optimized production GPT implementation.
- No KV cache is implemented yet.
- No tokenizer or training pipeline is included yet.
- Model quality depends heavily on dataset, tokenizer, model scale,
  training objective, and compute.