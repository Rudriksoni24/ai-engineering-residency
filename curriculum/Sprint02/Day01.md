# Sprint 2 — Day 1

# Local LLM Architecture and Runtime Landscape

## Goal

Understand how a local LLM moves from model files to application output.

Establish a runtime abstraction that allows the application layer to
remain independent of the underlying inference runtime.

## Learning Objectives

By the end of this day, I should be able to explain:

- What an LLM runtime does.
- The difference between a model and a runtime.
- The difference between Ollama and llama.cpp.
- What happens during local inference.
- What model weights, tokenizer, context window, and KV cache do.
- Why quantization is required for local inference.
- Why an application should avoid depending directly on one runtime.

## Architecture

Application
    ↓
Runtime Abstraction
    ↓
Inference Runtime
    ↓
Model + Tokenizer + Configuration
    ↓
Hardware Backend
    ↓
Generated Tokens

## Deliverables

- [ ] Local LLM architecture document.
- [ ] Runtime abstraction.
- [ ] Runtime request and response contracts.
- [ ] Runtime comparison report.
- [ ] Architecture decision record.
- [ ] Unit tests.
- [ ] Scoreboard updated.

## Reading

- Ollama documentation - https://docs.ollama.com/?utm_source=chatgpt.com 
- llama.cpp documentation - https://github.com/ggml-org/llama.cpp?utm_source=chatgpt.com 
- llama.cpp model and GGUF documentation - https://github.com/ggml-org/llama.cpp/blob/master/docs/models.md?utm_source=chatgpt.com

## Definition of Done

- [ ] Can explain the full local inference path.
- [ ] Can distinguish model, runtime, and application.
- [ ] Runtime interface is implemented.
- [ ] Runtime-specific code is not exposed to application code.
- [ ] Tests pass.