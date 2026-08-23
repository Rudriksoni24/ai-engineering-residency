# Week 2 Day 2

# Multi-Head Attention

## Goal

Understand and implement multi-head attention by combining multiple
independent attention heads.

## Duration

- Theory: 25 minutes
- Implementation: 95 minutes

## Learning Objectives

By the end of this lab, I should be able to:

- Explain the limitation of a single attention head.
- Explain why multiple attention heads are useful.
- Split embeddings across multiple heads.
- Perform scaled dot-product attention per head.
- Concatenate head outputs.
- Apply an output projection.
- Track tensor shapes throughout the operation.

---

## Read

Attention Is All You Need

Section 3.2.2 — Multi-Head Attention

https://arxiv.org/abs/1706.03762

---

## Core Formula

MultiHead(Q, K, V) =
Concat(head₁, ..., headₕ)Wᴼ

where:

headᵢ = Attention(QWᵢQ, KWᵢK, VWᵢV)

---

## Implement

- Configurable number of heads
- Q projection
- K projection
- V projection
- Head splitting
- Scaled dot-product attention per head
- Head concatenation
- Output projection

---

## Constraints

d_model must be divisible by num_heads.

---

## Tests

- Correct output shape
- Correct number of heads
- Invalid head configuration raises an error
- Attention weights have expected shape
- Causal masking works with multiple heads
- Output projection preserves d_model

---

## Questions

1. Why use multiple heads instead of one larger attention operation?
2. Why does d_model need to be divisible by num_heads?
3. What does each head learn?
4. Why concatenate before applying Wᴼ?
5. How does multi-head attention affect computation?
6. Why are separate Q, K, and V projections needed per head?

---

## Deliverables

- [ ] Multi-head attention implementation
- [ ] Shape tracing
- [ ] Attention visualization
- [ ] Causal mask support
- [ ] Tests
- [ ] README
- [ ] ADR
- [ ] Scoreboard updated
- [ ] Merged to main