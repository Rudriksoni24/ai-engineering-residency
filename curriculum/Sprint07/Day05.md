# Sprint 7 — Day 5: RLHF Concepts

## Artifact

Alignment Architecture Notes

## Purpose

Understand the architecture of RLHF and reward modeling at a systems level.

Today is not a production RLHF training day.

The objective is to understand the moving parts and failure modes.

---

## Canonical Alignment Flow

```text
Base Model
   ↓
Supervised Fine-Tuning
   ↓
Preference Data
   ↓
Reward Model
   ↓
RL Optimization
   ↓
Aligned Policy