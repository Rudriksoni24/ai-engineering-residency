# Sprint 3 Day 5 — End-to-End RAG Pipeline

## Objective

Build a complete local Retrieval-Augmented Generation application.

## Architecture

Document
    ↓
Load
    ↓
Normalize
    ↓
Chunk
    ↓
Embed
    ↓
Vector Store

User Query
    ↓
Embed
    ↓
Retrieve
    ↓
Prompt Builder
    ↓
Local LLM
    ↓
Answer + Sources

## Components

### Document Pipeline
- **Loader:** Custom text file reader targeting policy documentation (`data/examples/reconciliation_policy.txt`).
- **Chunking:** Document split into discrete thematic segments optimized for financial compliance text retrieval.

### Embedding Model
- **Model:** Hugging Face local embedding model loaded from the Hub to compute dense vector representations for queries and context chunks.

### Local LLM
- **Runtime:** `OllamaRuntime` class sending HTTP REST requests via `requests` to an independent local Ollama service (`http://localhost:11434/api/generate`).
- **Generation:** Non-streaming context generation utilizing strict parameter controls passed through custom `GenerationRequest` contracts.

### Retrieval Strategy
Top-K cosine similarity retrieval.

## Experiments

### Question 1 — Direct Match

Question:
How should transaction mismatches be handled?

Retrieved Context:
Reconciliation policies and transaction parsing guidelines found in `data/examples/reconciliation_policy.txt` across 3 active chunks.

Answer:
Transaction mismatches should be identified and handled by a reconciliation system, which looks for missing transactions, duplicate transactions, amount mismatches, and currency issues.

Sources:
- data/examples/reconciliation_policy.txt (Retrieved chunks: 3)

Correct:
Yes. The model successfully identified explicit steps for handling mismatches using the designated context document.

### Question 2 — Semantic Match

Question:
What is the process for investigating inconsistent transactions?

Retrieved Context:
Reconciliation workflow descriptions located within `data/examples/reconciliation_policy.txt` across 3 active chunks.

Answer:
The process for investigating inconsistent transactions involves identifying the following issues: missing transactions, duplicate transactions, amount mismatches, and currency mismatches. These issues are typically identified by a reconciliation system comparing records between multiple financial systems.

Sources:
- data/examples/reconciliation_policy.txt (Retrieved chunks: 3)

Correct:
Yes. The model understood "inconsistent transactions" as a semantic proxy for "mismatches" and correctly isolated the corresponding processing pipeline steps.

### Question 3 — Unknown Answer

Question:
What is the CEO's name?

Behavior:
The model correctly adhered to the grounding strategy constraints. Since the information did not reside anywhere within the context documents, it exited gracefully with a fallback response rather than hallucinating a name.

Answer:
I don't know based on the provided documents.

Sources:
- data/examples/reconciliation_policy.txt (Retrieved chunks: 3)

## Grounding Strategy

- Answer using retrieved context only.
- Preserve source information.
- Return deterministic fallback when no context exists.

## Limitations

- In-memory vector store.
- No relevance threshold.
- No reranking.
- No hybrid search.
- No structured citations.
- No retrieval evaluation dataset.
- Prompt instructions alone cannot guarantee factuality.

## Key Learnings
- **Abstract Defensively:** Creating structured code signatures using abstract classes (`LLMRuntime`) ensures strict interface compliance across runtimes, though runtime concrete bindings must be strictly managed when instantiating internal tools.
- **Grounding works via API boundaries:** Setting clear system parameters forces small local models to adhere to missing-context constraints ("I don't know based on the provided documents") instead of filling out gaps with training weights.
- **Environment Isolation matters:** Hugging Face caching rules and API keys (`HF_TOKEN`) affect initial cold start setup even when the final runtime (Ollama) operates entirely offline on a developer's desktop loop.
