# Local LLM Architecture

## Purpose

Provide a runtime-independent interface for applications that need to
perform local language model inference.

## System Layers

### Application Layer

Examples:

- RAG systems
- Agents
- Banking applications
- APIs
- Evaluation systems

The application should not contain runtime-specific HTTP calls.

### Runtime Abstraction Layer

Provides a stable interface for:

- Generation
- Health checks
- Future streaming
- Future embeddings
- Future structured outputs

### Runtime Layer

Initial runtimes:

- Ollama
- llama.cpp

Future runtimes may include specialized local or cluster inference
systems.

### Model Layer

Contains:

- Model weights
- Tokenizer
- Model configuration
- Chat template
- Context configuration

### Hardware Layer

Responsible for executing model operations using:

- Apple Silicon acceleration
- CPU
- GPU
- Future Kubernetes/cluster infrastructure

## Request Flow

User Request
    ↓
Application
    ↓
LLMRuntime
    ↓
Runtime Adapter
    ↓
Inference Runtime
    ↓
Tokenizer
    ↓
Model Forward Pass
    ↓
Next Token Selection
    ↓
Repeated Autoregressive Generation
    ↓
Response
## Ollama Runtime Implementation

The first concrete runtime implementation is OllamaRuntime.

Flow:

Application
    ↓
GenerationRequest
    ↓
LLMRuntime
    ↓
OllamaRuntime
    ↓
POST /api/generate
    ↓
Ollama
    ↓
Local Model
    ↓
GenerationResponse

The application does not construct Ollama HTTP requests directly.

## llama.cpp Runtime

llama.cpp is evaluated as a lower-level local inference runtime.

Flow:

Application
    ↓
Runtime Adapter
    ↓
llama.cpp CLI or Server
    ↓
GGUF Model
    ↓
Local Hardware

The initial implementation experiments with CLI and server modes before finalizing the production runtime adapter.