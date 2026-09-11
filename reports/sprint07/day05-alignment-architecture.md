# Sprint 7 — Day 5 Report

## Title

RLHF Concepts

## Artifact

Alignment Architecture Notes

## Objective

Understand RLHF architecture, reward models, preference data, PPO at a
systems level, KL control, and common alignment failure modes.

## Canonical Architecture

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