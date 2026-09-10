# Sprint 7 — Day 1: Fine-Tuning Fundamentals

## Artifact

Fine-Tuning Study Lab

## Learning Objectives

By the end of this day I should be able to explain:

1. Pretraining vs fine-tuning.
2. What full fine-tuning changes.
3. Forward passes.
4. Loss functions.
5. Backpropagation.
6. Optimizer steps.
7. Training loops.
8. Dataset examples, batches, and epochs.
9. Learning rate.
10. Gradient accumulation.
11. Total vs trainable parameter counts.
12. Model-weight memory.
13. Gradient memory.
14. Optimizer-state memory.
15. Activation memory.
16. Why full fine-tuning is expensive.
17. Prompting vs RAG vs fine-tuning.

## Core Training Loop

A simplified supervised training iteration is:

```text
input
  ↓
forward pass
  ↓
prediction
  ↓
loss(prediction, target)
  ↓
backward()
  ↓
gradients
  ↓
optimizer.step()
  ↓
updated parameters