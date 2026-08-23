# First principle: Model ≠ Runtime

Model = Weights + architecture + tokenizer/configuration

Runtime = Software that loads the model and executes inference

Application = Your RAG system, agent, API, banking application, etc.

# Local LLM Systems

This module contains infrastructure for running and integrating local
language models.

## Architecture

Application
    ↓
Runtime Abstraction
    ↓
Runtime Adapter
    ↓
Local Inference Runtime
    ↓
Model

## Initial Runtimes

- Ollama
- llama.cpp

## Design Principle

Application code should depend on a stable runtime contract rather than
a specific inference implementation.

## Sprint Roadmap

### Day 1

Architecture and runtime abstraction.

### Day 2

Ollama installation, local models, and first runtime adapter.

### Day 3

Model anatomy and quantization.

### Day 4

Streaming and structured inference.

### Day 5

llama.cpp and GGUF.

### Day 6

Local LLM service.

### Day 7

Integration and benchmarking.

## Model Analysis

The local-llm module includes tools for estimating approximate model
weight memory.

The current estimator considers:

- Parameter count
- Precision / quantization

The estimator does not yet accurately calculate:

- KV cache memory
- Runtime-specific memory
- Temporary inference buffers
- Hardware-specific memory allocation

These will be explored in later iterations.