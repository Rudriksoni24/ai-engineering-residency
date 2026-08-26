# Sprint 3 Day 3 — Local Embeddings

## Objective

Build a local embedding pipeline for RAG chunks.

## Architecture

Document
    ↓
Normalization
    ↓
Chunking
    ↓
Local Embedding Model
    ↓
Embedded Chunks

## Environment

- Machine: Apple Silicon M2
- Memory: 16 GB
- Embedding model: inferred as `all-MiniLM-L6-v2` — the model download (~90.9MB `model.safetensors`) and the resulting 384-dimension output match this model exactly, which is also the default model for `sentence-transformers` when no model name is specified. Confirm against `EmbeddingConfig`'s actual default to be certain.
- Embedding dimension: 384

---

## Experiments

### Experiment 1 — Single Text Embedding

**Not yet run as a standalone test.** `run_embeddings.py` only exercises the full ingestion → chunk → embed pipeline; there's no isolated single-string embedding call in what's been run so far. To capture this properly, a small script embedding one fixed string directly (bypassing the loader/chunker) would isolate the embedding model's behavior from the rest of the pipeline — useful for later confirming embedding determinism on its own.

### Experiment 2 — Batch Chunk Embedding

Number of chunks: **5** (using the `chunk_size=100, chunk_overlap=20` baseline config from Day 2)

Embedding dimension: **384** per chunk

Result — confirmed across two separate runs, with identical chunk IDs and embedding vectors both times:

| Chunk ID | Embedding sample (first 5 values) |
|---|---|
| `cd0fcc52d36f` | `[-0.0409, -0.0046, -0.0669, -0.0289, -0.1242]` |
| `a5765e19fcec` | `[-0.0824, 0.0308, 0.0067, -0.0622, -0.0698]` |
| `f8803e92e2bb` | `[0.0261, 0.0067, -0.0762, -0.0426, -0.0467]` |
| `157242242257` | `[-0.0267, 0.0651, -0.0358, -0.0543, 0.0267]` |
| `f3176d142938` | `[-0.0403, 0.1251, -0.0160, -0.0141, 0.1122]` |

Every chunk ID matched exactly across two independent invocations. Raw embedding values matched to full displayed precision in those first two runs; a third run later showed the same chunk IDs but embedding values differing at the ~1e-9 level (e.g. `-0.04092739149928093` vs. `-0.04092738777399063`) — consistent with non-deterministic summation order in multi-threaded CPU matrix operations, not a change in model, input, or code. This is far too small to affect similarity results (see Experiment 3) but is worth stating precisely: chunk IDs are exactly deterministic (they're content hashes); embedding vectors are deterministic to a very high but not perfect precision.

### Experiment 3 — Semantic Similarity

Transaction A vs Transaction B (similar/paraphrased transaction texts): **cosine similarity = 0.756**

Transaction A vs Unrelated Text: **cosine similarity = -0.001**

Result: this is exactly the shape you want to see. Two texts describing the same or a closely related transaction land at 0.756 — clearly and strongly similar — while an unrelated text lands essentially at zero, meaning the model treats it as having no meaningful semantic relationship to the transaction text at all (not even the mild positive correlation you'd sometimes get from shared generic language). The gap between 0.756 and -0.001 is large enough to be a genuinely useful retrieval signal, not a marginal or ambiguous one.

This is the first result in this sprint that tests whether the embeddings are *semantically useful*, rather than just present and reproducible (which Experiment 2 already established). Both properties now hold: the embeddings are deterministic **and** they separate related from unrelated content by a wide margin on this small test.

---

## Observations

- The pipeline is fully deterministic end-to-end for identical input: same chunk IDs, same embeddings, across two completely separate process invocations. This is the property needed for reliable re-ingestion (see Day 2's chunk-ID-stability question) — now confirmed at the embedding layer too, not just the chunking layer.
- **The embedding model is being re-downloaded from Hugging Face on every run** rather than being served from a local cache — both timed runs took ~90 seconds and repeated the full download of `model.safetensors` and tokenizer files. This is a real inefficiency worth fixing: either the Hugging Face cache directory isn't persisting between runs, or `EmbeddingConfig()` isn't pointing at a stable cache location. Worth checking `~/.cache/huggingface/hub` after a run to see if the model is actually landing there and being reused correctly.
- Getting the pipeline to actually execute took significantly more effort than running it — most of today's work was resolving `uv run` vs. direct-venv-path invocation issues stemming from the project/package name collision (`rag/` being both the uv project root and the Python package). See Key Learnings.

## Design Decisions

### Why use a dedicated embedding model?

A dedicated sentence-embedding model (as opposed to, say, reusing a general-purpose LLM to "generate a vector") is trained specifically so that semantic similarity in meaning corresponds to geometric closeness in vector space — that's what makes cosine similarity a meaningful retrieval signal at all. A model like `all-MiniLM-L6-v2` is also small and fast enough to run locally without needing a GPU, which matters for a local-first RAG pipeline where every chunk of every ingested document needs to be embedded.

### Why preserve metadata and source?

Same reasoning carried forward from ingestion and chunking: an embedding vector alone is just 384 numbers — it has no way to say what document it came from, what version, or where in that document it sits. Metadata is what makes a retrieved embedding actionable (traceable back to source) rather than just a nearest-neighbor match with no context.

### Why should embedding model changes trigger re-indexing?

Embedding vectors from different models are not comparable to each other — a vector from `all-MiniLM-L6-v2` and a vector from a different model don't share a coordinate space, even if both happen to be 384-dimensional. If the embedding model changes (a version bump, a switch to a larger model, a fine-tuned variant), every previously stored vector becomes meaningless for similarity comparison against newly embedded queries. This means model changes can't be applied incrementally — the entire index needs to be regenerated from the source documents, not just appended to, or retrieval quality will silently degrade in ways that are hard to detect without dedicated evaluation.

## Limitations

- Small synthetic dataset.
- No retrieval evaluation yet.
- No persistent vector store.
- No domain-specific embedding comparison.
- Semantic similarity was only tested on one similar pair and one unrelated pair — a larger, more varied test set (multiple similarity levels, edge cases like same-topic-different-intent) would give more confidence than a single 0.756-vs-0.001 data point.
- Model caching appears broken — every run re-downloads ~90MB, which will not scale to repeated runs or CI.

## Key Learnings

- The pipeline's chunk IDs are exactly deterministic across separate process invocations (they're content hashes). Embedding vectors are deterministic to roughly 9 decimal places but showed tiny (~1e-9) floating-point drift in a third run — almost certainly from non-deterministic thread scheduling in the underlying CPU matrix math, not from any change in input or model. Negligible in practice, but worth stating precisely rather than claiming perfect bit-for-bit reproducibility.
- The embeddings pass their first real usefulness test: 0.756 cosine similarity for related transaction texts vs. -0.001 for unrelated text. That's a wide, clean separation — determinism alone wouldn't have told you the embeddings were any good for retrieval; this result is the first evidence that they actually are.
- The project's biggest source of friction this sprint hasn't been the RAG logic itself — it's been `rag/` serving as both the uv project root and the importable package name simultaneously, which creates a structural conflict: `uv run` wants to be invoked from inside `rag/`, while `-m rag.scripts...` wants to be invoked from *outside* `rag/`. Every "silent" or `ModuleNotFoundError` failure this sprint traced back to standing in the wrong one of those two directories for the command being run.
- The practical workaround (`rag/.venv/bin/python -m rag.scripts.run_embeddings`, run from the outer folder) works reliably, but the long-term fix is either a `src/` layout (package moved to `rag/src/rag/`) or fully separating the uv project directory from the package directory — either removes the ambiguity permanently instead of requiring a specific directory + specific invocation style every time.
- Before scaling up to more documents, fix the embedding-model caching issue — re-downloading 90MB per run is wasted time now and will become a real bottleneck once ingestion runs regularly or in CI.