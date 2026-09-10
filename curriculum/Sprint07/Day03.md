# Sprint 7 — Day 3: PEFT and Local Fine-Tuning

## Artifact

Adapted Local Model

## Purpose

Use PEFT to perform a small real LoRA adaptation of a pretrained local
causal language model.

## Learning Objectives

By the end of today I should understand:

1. How PEFT maps onto the LoRA mathematics implemented on Day 2.
2. How to select LoRA target modules.
3. How to configure rank, alpha, and dropout.
4. How PEFT freezes the base model.
5. How to inspect total and trainable parameters.
6. How to train only adapter parameters.
7. How to save an adapter independently of the base model.
8. How to load the base model and adapter again.
9. How to compare inference before and after adaptation.
10. Why deterministic seeds matter.
11. Local-training limitations on Apple Silicon.
12. The difference between adapter artifacts and complete model weights.

---

## Day 2 to Day 3 Mapping

Day 2 implemented:

```text
W' = W + ΔW

ΔW = BA