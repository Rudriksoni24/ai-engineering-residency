# Sprint 7 — Day 2: LoRA Mathematics and Architecture

## Artifact

LoRA Implementation

## Learning Objectives

By the end of today I should understand:

1. Why full fine-tuning is expensive.
2. Why parameter-efficient adaptation exists.
3. The LoRA update equation.
4. Frozen base weights.
5. Low-rank matrices A and B.
6. Rank r.
7. LoRA alpha.
8. LoRA scaling.
9. LoRA initialization.
10. Trainable parameter reduction.
11. Merged vs unmerged adapters.
12. Where LoRA is commonly applied.
13. Attention projection adaptation.
14. Why low-rank updates can work.

---

## Starting Point

For a standard linear layer:

```text
y = Wx + b