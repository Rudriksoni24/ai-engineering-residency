# Week 2 Day 4

# Attention Is All You Need — Deep Dive

## Goal

Deeply understand the original Transformer architecture described in
"Attention Is All You Need" and map the concepts from the paper to the
implementations completed in Week 2 Days 1–3.

This day focuses on understanding architecture and identifying gaps
between the original Transformer and the components implemented so far.

## Duration

- Paper study: 60 minutes
- Architecture mapping: 40 minutes
- Notes and validation: 20 minutes

---

# Primary Resource

Attention Is All You Need

https://arxiv.org/abs/1706.03762

---

# Learning Objectives

By the end of this day, I should be able to:

- Explain the original Transformer architecture.
- Explain why the Transformer replaced recurrence with attention.
- Explain self-attention mathematically.
- Explain scaled dot-product attention.
- Explain multi-head attention.
- Explain positional encoding.
- Explain residual connections and LayerNorm.
- Explain the position-wise feed-forward network.
- Explain encoder self-attention.
- Explain decoder masked self-attention.
- Explain encoder-decoder attention.
- Identify which parts I have already implemented.
- Identify which parts remain before building MiniGPT.

---

# Paper Reading Order

## Section 1 — Introduction

Focus on:

- Why recurrent models were limited.
- Why sequential computation creates a bottleneck.
- Why attention allows greater parallelization.

Question:

Why is removing recurrence useful for modern hardware?

---

## Section 2 — Background

Understand:

- Self-attention
- Recurrent architectures
- Convolutional architectures

Question:

What problem does self-attention solve differently from RNNs?

---

## Section 3.1 — Encoder and Decoder Stacks

Understand:

- Encoder structure
- Decoder structure
- Stacking N layers
- Residual connections
- Layer normalization

Do not implement a complete encoder-decoder stack today.

The goal is architectural understanding.

---

## Section 3.2 — Attention

Understand:

Attention(Q, K, V) =
softmax(QKᵀ / √dₖ)V

Explain:

- Query
- Key
- Value
- Attention scores
- Scaling factor
- Softmax
- Weighted values

---

## Section 3.2.2 — Multi-Head Attention

Understand:

MultiHead(Q, K, V) =
Concat(head₁, ..., headₕ)Wᴼ

Question:

Why project Q, K, and V into multiple representation subspaces?

---

## Section 3.2.3 — Applications of Attention

Understand the difference between:

1. Encoder self-attention
2. Decoder self-attention
3. Encoder-decoder attention

Create diagrams for all three.

---

## Section 3.3 — Position-wise Feed-Forward Networks

Understand:

FFN(x) =
max(0, xW₁ + b₁)W₂ + b₂

Question:

Why does every token use the same FFN architecture while still
producing different outputs?

---

## Section 3.4 — Embeddings and Softmax

Understand:

- Input embeddings
- Output embeddings
- Weight sharing

Document what this means conceptually.

---

## Section 3.5 — Positional Encoding

Understand:

- Why attention alone does not provide token order.
- Sinusoidal positional encoding.
- Why sine and cosine functions are used.
- How positional information is combined with embeddings.

---

# Architecture Mapping

Map each concept to repository code.

| Paper Concept | Repository Implementation | Status |
|---|---|---|
| Embeddings | Previous Week implementation | Complete |
| Positional Encoding | Previous Week implementation | Complete |
| Scaled Dot-Product Attention | Week 2 Day 1 | Complete |
| Causal Mask | Week 2 Day 1 | Complete |
| Multi-Head Attention | Week 2 Day 2 | Complete |
| Feed-Forward Network | Week 2 Day 3 | Complete |
| Residual Connections | Week 2 Day 3 | Complete |
| LayerNorm | Week 2 Day 3 | Complete |
| Transformer Block | Week 2 Day 3 | Complete |
| Transformer Stack | Not implemented | Pending |
| Encoder-Decoder Cross-Attention | Not implemented | Not required for MiniGPT |
| Tokenizer | Pending | Required for MiniGPT |
| Language Model Head | Pending | Required for MiniGPT |
| Training Loop | Pending | Required for MiniGPT |
| Text Generation | Pending | Required for MiniGPT |

---

# Implementation Review

Review the previous labs:

- Self-Attention
- Multi-Head Attention
- Transformer Block

For each implementation answer:

1. Which equation from the paper does this implement?
2. What are the input tensor shapes?
3. What are the output tensor shapes?
4. Which parameters are trainable?
5. How does gradient flow through the component?
6. What simplifications did the implementation make?

---

# Architecture Diagram

Draw the original Transformer architecture:

Input
  ↓
Embedding + Positional Encoding
  ↓
Encoder Stack
  ↓
Encoder Representations
  ↓
Decoder Cross-Attention
  ↑
Masked Decoder Self-Attention
  ↑
Output Tokens
  ↓
Linear
  ↓
Softmax

Then draw the architecture needed for a GPT-style model:

Input Tokens
  ↓
Token Embeddings
  +
Positional Embeddings
  ↓
Decoder-Only Transformer Blocks
  ↓
LayerNorm
  ↓
Language Model Head
  ↓
Vocabulary Logits
  ↓
Next Token

---

# Comparison Exercise

Create a comparison table.

Compare:

- Original Transformer
- Encoder-only model
- Decoder-only model

Focus on:

- Attention type
- Causal masking
- Primary use
- Input/output behavior
- Text generation capability

---

# Self-Check Questions

Answer without looking at notes:

1. Why did the original Transformer remove recurrence?

2. Why is attention scaled by √dₖ?

3. Why does the decoder require causal masking?

4. Why does the encoder not require causal masking?

5. What is the difference between self-attention and cross-attention?

6. Why is positional information required?

7. What happens if positional encoding is removed?

8. Why are residual connections used?

9. Why does the FFN operate independently on each position?

10. What does stacking Transformer layers achieve?

11. Why is the original Transformer architecture not the same as GPT?

12. Which components are still missing before we can train a MiniGPT?

---

# Deliverables

- [ ] Paper notes
- [ ] Architecture mapping
- [ ] Original Transformer diagram
- [ ] GPT-style architecture diagram
- [ ] Encoder vs decoder comparison
- [ ] Implementation gap analysis
- [ ] Self-check questions answered
- [ ] ADR completed
- [ ] Scoreboard updated
- [ ] Feature branch pushed
- [ ] Merged to main

---

# Definition of Done

The day is complete only when:

- [ ] I can explain Q, K, and V without notes.
- [ ] I can derive scaled dot-product attention.
- [ ] I can explain multi-head attention.
- [ ] I can explain causal masking.
- [ ] I can draw the original Transformer.
- [ ] I can explain why GPT is decoder-only.
- [ ] I know exactly what is missing before building MiniGPT.
- [ ] All notes are committed.