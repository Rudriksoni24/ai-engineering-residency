# Sprint 2 — Day 3

# Model Anatomy, Memory, Context Windows and Quantization

## Goal

Understand what makes an LLM consume memory and how model size,
quantization, and context length affect local inference.

## Learning Objectives

By the end of this day, I should be able to explain:

- Parameters and model size.
- Model weights.
- FP32, FP16, BF16 and low-bit quantization.
- Why parameter count is not the complete memory requirement.
- Context windows.
- KV cache.
- Why longer context increases inference memory usage.
- The relationship between model format and runtime.
- The role of GGUF in local inference.

## Deliverables

- [ ] Model profile data structure.
- [ ] Memory estimation utility.
- [ ] Quantization comparison.
- [ ] At least three model profiles.
- [ ] Local hardware analysis.
- [ ] Unit tests.
- [ ] Model comparison report.

## Definition of Done

- [ ] Can estimate approximate weight memory.
- [ ] Can explain why actual memory is larger than weight memory.
- [ ] Can explain KV cache.
- [ ] Can compare at least three quantization levels.
- [ ] Can justify model selection for a 16 GB M2 Mac.