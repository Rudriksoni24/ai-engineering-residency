# Week 2 Day 1

# Self-Attention: Query, Key, Value

## Goal

Understand and implement scaled dot-product self-attention.

## Duration

- Theory: 30 minutes
- Implementation: 90 minutes

## Learning Objectives

By the end of this lab, I should be able to:

- Explain Query, Key, and Value.
- Implement numerically stable softmax.
- Implement scaled dot-product attention.
- Understand attention matrix shapes.
- Explain why attention scores are scaled.
- Implement causal masking.
- Explain why GPT-style models require causal attention.

---

## Read

### Attention Is All You Need

Read:

Section 3.2.1 — Scaled Dot-Product Attention

https://arxiv.org/abs/1706.03762

---

## Formula

Attention(Q, K, V) = softmax(QKᵀ / √dₖ)V

---

## Implement

- Numerically stable softmax
- Query, Key, Value matrices
- Attention score calculation
- Scaling
- Softmax attention weights
- Attention output
- Causal masking

---

## Experiments

Compare:

- Unscaled attention
- Scaled attention

Experiment with:

- dₖ = 8
- dₖ = 64
- dₖ = 512

Observe how scaling affects the softmax distribution.

---

## Visualization

Generate:

- Attention matrix
- Causal attention matrix
- Unmasked vs masked attention comparison

---

## Tests

- Softmax probabilities sum to 1.
- Softmax is numerically stable.
- Attention output shape is correct.
- Attention weights shape is correct.
- Each attention row sums to approximately 1.
- Causal masking blocks future tokens.
- Masked future probabilities are approximately zero.

---

## Questions

1. Why are Q, K, and V separate representations?
2. What does QKᵀ represent?
3. Why divide by √dₖ?
4. Why apply softmax?
5. Why does every attention row sum to 1?
6. Why does GPT require causal masking?
7. What happens if masking is applied after softmax?

---

## Deliverables

- [ ] Stable softmax
- [ ] Scaled dot-product attention
- [ ] Causal masking
- [ ] Scaling experiment
- [ ] Attention visualization
- [ ] Tests
- [ ] README
- [ ] ADR
- [ ] Scoreboard updated
- [ ] Feature branch pushed
- [ ] Merged to main