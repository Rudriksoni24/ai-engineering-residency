# Week 2 Day 3

# Transformer Block

## Goal

Build a complete Transformer block by combining multi-head self-attention,
residual connections, layer normalization, and a position-wise feed-forward
network.

The goal is to understand how the individual components implemented in the
previous days work together as a reusable Transformer layer.

## Duration

- Theory: 30 minutes
- Implementation: 90 minutes

## Learning Objectives

By the end of this lab, I should be able to:

- Explain the architecture of a Transformer block.
- Implement a position-wise feed-forward network.
- Integrate multi-head self-attention.
- Implement residual connections.
- Apply Layer Normalization.
- Explain the difference between attention and feed-forward computation.
- Trace tensor shapes through the entire Transformer block.
- Verify gradient flow through all major components.
- Support causal masking.

---

# Read

## Attention Is All You Need

Read the following sections:

- Section 3.1 — Encoder and Decoder Stacks
- Section 3.3 — Position-wise Feed-Forward Networks
- Section 3.4 — Embeddings and Softmax

https://arxiv.org/abs/1706.03762

## Layer Normalization

Review the PyTorch documentation:

https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html

---

# Architecture

The Transformer block implemented today follows the original
post-normalization structure.

```text
Input
  │
  ▼
Multi-Head Self-Attention
  │
  ▼
Residual Connection
  │
  ▼
Layer Normalization
  │
  ▼
Feed-Forward Network
  │
  ▼
Residual Connection
  │
  ▼
Layer Normalization
  │
  ▼
Output
Mathematically:
x = LayerNorm(x + MultiHeadAttention(x))

output = LayerNorm(x + FeedForward(x))