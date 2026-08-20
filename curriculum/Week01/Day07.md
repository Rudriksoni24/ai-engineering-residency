# Week 1 — Day 7

## Positional Encoding

### Goal

Understand why Transformers need positional information and implement sinusoidal positional encoding from scratch.

### Time

* Theory: 30 minutes
* Implementation: 90 minutes

## Learning Objectives

By the end of this lab, I should be able to:

* Explain why attention does not inherently understand token order.
* Explain positional embeddings versus positional encoding.
* Implement sinusoidal positional encoding.
* Add positional encoding to token embeddings.
* Visualize positional encoding.
* Explain why different frequencies are used across embedding dimensions.

## Read

### Attention Is All You Need

Read only:

* Section 3.5: Positional Encoding

https://arxiv.org/abs/1706.03762

### PyTorch Transformer Documentation

Review positional encoding-related examples and Transformer concepts:

https://pytorch.org/docs/stable/generated/torch.nn.Transformer.html

## Build

### Task 1 — Order Experiment

Create two sequences containing the same tokens in different positions.

Demonstrate that token embeddings alone do not encode sequence order.

### Task 2 — Sinusoidal Positional Encoding

Implement the positional encoding equations from the Transformer paper.

For position `pos` and dimension index `i`:

```text
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))

PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

### Task 3 — Add Position to Embeddings

Generate sample token embeddings and add positional encoding:

```text
Token Embedding
       +
Positional Encoding
       =
Position-Aware Embedding
```

### Task 4 — Visualization

Visualize positional encodings as a matrix.

Experiment with:

* Maximum sequence length
* Embedding dimension
* Different token positions

### Task 5 — Tests

Test:

* Output shape
* Position zero
* Different positions produce different encodings
* Same configuration produces deterministic output
* Positional encoding can be added to embeddings

## Questions

Answer these in the README:

1. Why can't self-attention determine token order by itself?
2. Why use sine and cosine?
3. Why are multiple frequencies used?
4. What is the difference between learned positional embeddings and sinusoidal encoding?
5. What happens when inference sequence length exceeds the training sequence length?
6. Why is positional information added rather than concatenated in the original Transformer?

## Deliverables

* [ ] Positional encoding implementation
* [ ] Embedding integration
* [ ] Visualization
* [ ] Tests
* [ ] README
* [ ] ADR
* [ ] Git commit
* [ ] Feature branch merged to main
