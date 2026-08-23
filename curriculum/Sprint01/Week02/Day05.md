# Week 2 Day 5

# MiniGPT Architecture

## Goal

Design and implement a small GPT-style decoder-only language model by
combining token embeddings, positional embeddings, stacked Transformer
blocks, final normalization, and a language model output head.

This day focuses on model architecture only.

Training will be implemented separately.

## Duration

- Architecture study: 25 minutes
- Implementation: 80 minutes
- Testing and documentation: 15 minutes

---

# Learning Objectives

By the end of this lab, I should be able to:

- Explain why GPT is decoder-only.
- Implement token embeddings.
- Implement positional embeddings.
- Combine token and positional representations.
- Stack Transformer blocks.
- Apply causal masking.
- Add a final LayerNorm.
- Add a language model head.
- Produce vocabulary logits.
- Trace tensor shapes through the complete model.
- Calculate the approximate parameter count.
- Verify gradient flow.

---

# Architecture

Input Token IDs

    ↓

Token Embedding

    +

Positional Embedding

    ↓

N Decoder Transformer Blocks

    ↓

Final LayerNorm

    ↓

Linear Language Model Head

    ↓

Vocabulary Logits

---

# Core Configuration

Start with:

- vocab_size = configurable
- d_model = 128
- num_heads = 4
- d_ff = 512
- num_layers = 4
- max_sequence_length = 64

These values should be configurable.

---

# Tensor Shapes

Input token IDs:

(batch, sequence_length)

Token embeddings:

(batch, sequence_length, d_model)

Positional embeddings:

(batch, sequence_length, d_model)

Transformer output:

(batch, sequence_length, d_model)

Vocabulary logits:

(batch, sequence_length, vocab_size)

---

# Tasks

## Task 1

Create a MiniGPTConfig.

The configuration should contain:

- vocab_size
- d_model
- num_heads
- d_ff
- num_layers
- max_sequence_length

---

## Task 2

Implement token embeddings.

Input:

(batch, sequence_length)

Output:

(batch, sequence_length, d_model)

---

## Task 3

Implement positional embeddings.

Generate position IDs:

0, 1, 2, ..., sequence_length - 1

Convert them to embeddings and add them to token embeddings.

---

## Task 4

Stack decoder-only Transformer blocks.

Each block must use causal self-attention.

---

## Task 5

Apply final LayerNorm.

---

## Task 6

Implement the language model head.

The head maps:

d_model → vocab_size

The output represents logits for every possible next token.

---

## Task 7

Implement shape tracing.

Document every tensor transformation.

---

## Task 8

Verify gradients.

Run backward propagation and verify that gradients reach:

- Token embeddings
- Positional embeddings
- Attention projections
- Feed-forward layers
- Final LayerNorm
- Language model head

---

# Tests

- [ ] Input/output shapes are correct.
- [ ] Different batch sizes work.
- [ ] Different valid sequence lengths work.
- [ ] Sequence length larger than max length fails.
- [ ] Causal masking is used.
- [ ] All major components receive gradients.
- [ ] Output vocabulary dimension is correct.

---

# Questions

1. Why is GPT decoder-only?

2. Why do we need token embeddings?

3. Why do we need positional embeddings?

4. What does a vocabulary logit represent?

5. Why do we use a linear layer before selecting the next token?

6. Why do we output logits instead of probabilities?

7. Why must causal masking exist during both training and generation?

8. What is the difference between model architecture and model training?

---

# Deliverables

- [ ] MiniGPTConfig
- [ ] MiniGPT model
- [ ] Token embeddings
- [ ] Positional embeddings
- [ ] Transformer stack
- [ ] Final LayerNorm
- [ ] Language model head
- [ ] Shape tracing
- [ ] Parameter count
- [ ] Gradient verification
- [ ] Unit tests
- [ ] README
- [ ] Architecture documentation
- [ ] ADR
- [ ] Scoreboard updated
- [ ] Merged to main