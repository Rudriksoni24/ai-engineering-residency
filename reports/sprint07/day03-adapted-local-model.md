# Sprint 7 — Day 3 Report

## Title

PEFT and Local Fine-Tuning

## Artifact

Adapted Local Model

## Objective

Perform a real resource-conscious local LoRA adaptation using a
pretrained Hugging Face causal language model and PEFT.

## Base Model

```text
HuggingFaceTB/SmolLM2-135M-Instruct

Configuration
LoRA rank: 4
LoRA alpha: 8
LoRA dropout: 0.05

Target modules:
- q_proj
- v_proj

Learning rate:
5e-4

Training steps:
20

Maximum sequence length:
128

Seed:
42

torch: 2.13.0
transformers: 5.16.1
peft: 0.20.0
accelerate: 1.15.0
