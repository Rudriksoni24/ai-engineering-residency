# Sprint 2 — Day 4

# Local Inference Engineering

## Goal

Extend the local LLM runtime to support production-style inference
patterns.

## Learning Objectives

By the end of this day, I should understand:

- Temperature.
- Token limits.
- Streaming.
- Structured output.
- Schema validation.
- The difference between valid JSON and valid application data.
- Why LLM output requires validation.
- Basic runtime failure handling.

## Deliverables

- [ ] Generation controls understood.
- [ ] Streaming contract designed.
- [ ] Ollama streaming implemented.
- [ ] Structured output contract created.
- [ ] Pydantic validation added.
- [ ] Invalid response handling tested.
- [ ] Integration experiment completed.

## Definition of Done

- [ ] Text can be streamed from the local model.
- [ ] Structured responses are validated.
- [ ] Invalid output does not silently enter the application.
- [ ] Unit tests pass.
- [ ] Integration test passes.