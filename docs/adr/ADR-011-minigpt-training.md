# ADR-011: MiniGPT Training Pipeline

## Status

Accepted

## Context

The MiniGPT architecture produces vocabulary logits but contains randomly
initialized parameters.

A training pipeline is required to learn statistical relationships from
data.

## Decision

Train the model using:

- Character-level tokenization
- Next-token prediction
- Cross entropy loss
- AdamW optimization
- Mini-batch training
- Checkpointing
- Autoregressive generation

## Why Character-Level Tokenization?

The objective of this implementation is to understand the complete
language model training pipeline with minimal tokenizer complexity.

This tokenizer is not intended for production-scale language models.

## Consequences

### Positive

- Entire training pipeline remains understandable.
- Easy to debug.
- Easy to validate through tiny-dataset overfitting.

### Negative

- Character-level tokenization is inefficient.
- Longer sequences are required.
- Results will not match modern LLM quality.