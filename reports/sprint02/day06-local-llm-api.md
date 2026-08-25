# Sprint 2 Day 6 — Local LLM API Service

## Architecture

Client
    ↓
FastAPI
    ↓
LLMService
    ↓
LLM Runtime
    ↓
Local Model

## Endpoints

| Endpoint | Purpose |
|---|---|
| GET /health | Liveness check |
| GET /ready | Runtime readiness |
| POST /v1/generate | Generate model output |

## Contracts

### GenerateRequest

done

### GenerateResponse

done

## Experiments

### Valid Generation Request

done

### Invalid Request

done

### Runtime Unavailable

done

## Key Learnings

FastAPI 
Service Layer
API decoupling
thread offloading
state isolation

## Design Decisions

### Why a service layer?

A service layer acts as an isolation barrier between your web framework (FastAPI) and your heavy machine learning execution logic (the LLM runtime).
Here is why this separation is critical for a local LLM application:

* Decouples HTTP from Logic: It isolates FastAPI components (like routing, JSON validation, and HTTP headers) from core model lifecycle logic. If you migrate from FastAPI to another framework (like Litestar, Sanic, or a gRPC server), your underlying LLMService logic remains entirely untouched.
* Encapsulates Heavy State & Lifecycle: Local LLMs require heavy object states, including memory arrays, context winders, and raw tokenizer weights. The service layer handles this state independently, preventing your API routing layer from bloating into a massive monolithic codebase.
* Abstracts Runtime Engines: It hides the complex internal mechanics of how text is generated. FastAPI simply calls .generate(), completely unaware of whether the backend runtime is running on Hugging Face Transformers, llama.cpp, vLLM, or ONNX Runtime.
* Enforces a Single Source of Truth: Centralizing your business logic ensures that inference rules, token-counting math, and safety guardrails are executed identically across all application endpoints.
* Simplifies Testing: You can easily isolate and unit test your text generation algorithms by mocking out the HTTP web requests entirely.

### Why dependency injection?

Dependency Injection (DI) allows FastAPI to efficiently manage the lifecycle of heavy local LLM resources by decoupling object creation from your route handlers.
Here is why using Dependency Injection is crucial for a local LLM service:

* Enforces Singleton Runtimes: Local LLMs consume gigabytes of VRAM and take significant time to load. DI ensures your LLMService is instantiated exactly once as a singleton, reusing the same model weights across all incoming HTTP requests instead of reloading them on every API call.
* Simplifies Testing and Mocking: You can easily swap out the heavy, hardware-dependent LLMService with a lightweight mock service during unit tests. This lets you test your API routing, validation, and error handling instantly without needing a GPU.
* Automates Lifecycle Management: FastAPI's Depends engine handles the setup and teardown of resources automatically. If your service requires database connections or configuration files, DI resolves these cascading dependencies cleanly.
* Improves Code Readability: Route handlers remain clean because they declare what dependencies they need as parameters, rather than containing complex code detailing how to initialize them.

### Why separate API and runtime contracts?

Separating API and runtime contracts creates a structural buffer that protects external API clients from changes made to the underlying machine learning backend.
Here is why this separation is vital for a local LLM application:

* Insulates Clients from Runtime Swaps: Your API contract (GenerateRequest/GenerateResponse) remains identical even if you completely switch your backend framework (e.g., migrating from Hugging Face transformers to llama.cpp or vLLM).
* Translates Schema Formats: The API contract handles user-friendly configurations (like system_prompt and user_message), which the service layer then transforms into specific runtime-required formats (like raw model prompt templates, token IDs, or engine-specific sampling parameters).
* Future-Proofs Versioning: You can upgrade, patch, or alter your internal model execution logic and runtime parameters without forcing everyone using your API to update their client code.
* Standardizes Validation: FastAPI cleanly handles client-side validation (like text length limits or bounding temperature values between 0.0 and 2.0) before the data ever touches the complex internal runtime data structures.

## Problems Encountered

model loading timeouts

## Next Improvements

Streaming tokens
request batching
structured JSON outputs