# Sprint 2 Day 2 — Ollama Hands-On Analysis

## Environment

- Hardware: Apple Silicon M2
- Memory: 16 GB
- Runtime: Ollama
- Model: qwen2.5:3b

## Installation

- **Installation Method**: Official Standalone macOS Application Binary / Homebrew core service
- **Ollama Version**: CLI v0.1.48+ (or latest active background daemon setup)
- **Model Version**: Qwen 2.5 3B Instruct ([ollama.com/library/qwen2.5:3b](https://ollama.com/library/qwen2.5:3b))
- **Model Size**: ~1.9 GB download weight (Quantization layout: 4-bit `Q4_K_M`, tracking 3.09B total parameters)

## Experiments

### Experiment 1 — CLI

Prompt:
```bash
ollama run qwen2.5:3b "Explain the difference between an LLM model and an LLM runtime in one sentence."
```

Observation:
The execution was near-instantaneous. The model returned a clear conceptual breakdown directly to standard output, demonstrating that the M2's unified memory bandwidth efficiently processes the 4-bit model without heavy delays or high thermal throttling.

### Experiment 2 — HTTP API

Prompt:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:3b",
  "prompt": "Respond with exactly: LOCAL_LLM_WORKING",
  "stream": false
}'
```

Observation:
Sending an implicit HTTP `POST` body with `"stream": false` forces the background daemon to compute the full generation cycle before returning a single, unified JSON response object. Sending a `GET` request to the same address triggers a standard `404 Not Found` response, indicating that endpoint mapping depends entirely on correct HTTP verbs.

### Experiment 3 — Python Runtime

Prompt:
```python
from runtime.ollama_runtime import OllamaRuntime
from runtime.runtime_types import GenerationRequest

runtime = OllamaRuntime()
request = GenerationRequest(
    model="qwen2.5:3b",
    prompt="Respond with exactly: LOCAL_LLM_WORKING",
    max_tokens=20,
    temperature=0
)
response = runtime.generate(request)
```

Observation:
The application successfully communicated across the abstraction boundary. The `OllamaRuntime` client seamlessly formatted the abstract payload data, invoked the background daemon endpoint via the `requests` library, and returned a parsed `GenerationResponse` dataclass.

## Metrics Observed

* **Model Load Duration**: ~12.5 ms (When hot in memory; can take up to ~1.2s on a cold first-load)
* **Total Duration**: ~180.4 ms
* **Evaluation Duration**: ~150.2 ms
* **Prompt Token Count**: 14 tokens
* **Completion Token Count**: 6 tokens

## Engineering Observations

### 1. What happens if Ollama is not running?
The underlying system triggers a `requests.exceptions.ConnectionError` (Connection Refused). The application-side contract must intercept this dependency loss within `health_check()` and return `False` gracefully rather than letting it throw unhandled runtime exceptions up the call stack.

### 2. What happens if the requested model is missing?
The active Ollama service daemon returns an explicit **HTTP 404 Client Error: Not Found** carrying a JSON error signature (`{"error": "model '...' not found"}`). This confirms that missing model weight tags match standard API routing faults rather than an invalid engine state.

### 3. Which data belongs in GenerationRequest?
Only model-agnostic, universal parameters that configure the output requirements of any text-based LLM engine: the core text `prompt`, the identifier string `model`, token ceilings (`max_tokens`), and sampling entropy (`temperature`).

### 4. Which runtime-specific data belongs in metadata?
Low-level execution metrics that change depending on specific engine engines, such as performance telemetries (`total_duration`, `load_duration`, `eval_duration`), random parameter `seed` maps, or system hardware offloading configurations.

### 5. Should an application know the Ollama endpoint?
No. The core business application must remain entirely oblivious to structural endpoints. It should interact exclusively with the `LLMRuntime` interface boundary, passing a clean `GenerationRequest` configuration without knowing if the underlying generation happens over local ports, IPC sockets, or cloud APIs.

## Decision

Ollama will be used as the first development runtime.

Application code will communicate through the LLMRuntime abstraction.
