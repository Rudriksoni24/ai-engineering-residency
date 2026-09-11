# Sprint 7 — Day 6: Direct Preference Optimization

## Artifact

Preference Optimization Lab

## Purpose

Understand why Direct Preference Optimization was introduced and how it
optimizes policy preferences directly from chosen/rejected response pairs.

DPO removes the need for an explicit learned reward-model plus PPO loop
in its basic training formulation.

---

## Traditional RLHF

A simplified RLHF pipeline is:

```text
Preference Data
      ↓
Reward Model
      ↓
PPO
      ↓
Policy