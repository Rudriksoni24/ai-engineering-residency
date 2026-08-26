# Sprint 3 Day 4 — Local Vector Storage and Retrieval

## Objective

Build a local vector store and semantic retrieval system.

## Architecture

Document
    ↓
Normalize
    ↓
Chunk
    ↓
Embed
    ↓
Vector Store
    ↓
Retriever
    ↓
Top-K Results

## Implementation

### Vector Store
- **Type**: In-memory storage.
- **Search Method**: Exact k-NN via linear scan (exhaustive search).
- **Persistence**: None (volatile lifecycle).

### Similarity Metric
Cosine similarity.

### Embedding Model
- **Source**: Hugging Face Hub (local deployment via `transformer` weights download).
- **Status**: Loaded successfully (103/103 weights tensors), running without localized API keys (`HF_TOKEN` warning noted).

### Vector Dimension
- Dense embeddings parameterized by the underlying Hugging Face transformer model architecture.

---

## Retrieval Experiments

### Query 1
* **Query**: How should transaction mismatches be investigated?
* **Expected Result**: Chunks covering reconciliation policies, mismatch identifications, and forensic handling.
* **Actual Top Result**: `ID: a5765e19fcec` (SOURCE: `data/examples/reconciliation_policy.txt`)
* **Content**: `A transaction mismatch does not automatically indicate fraud. A reconciliation system should identif`
* **Score**: 0.7549
* **Evaluation**: **Correct** (High semantic overlap regarding transaction mismatches).

### Query 2
* **Query**: What are examples of reconciliation problems?
* **Expected Result**: Chunks listing explicit issue categories (e.g., missing transactions, duplicates, amount/currency mismatches).
* **Actual Top Result**: `ID: cd0fcc52d36f` (SOURCE: `data/examples/reconciliation_policy.txt`)
* **Content**: `Transaction reconciliation compares records between multiple financial systems. A transaction mismat`
* **Score**: 0.4573
* **Evaluation**: **Incorrect / Suboptimal** (Retrieved a high-level definition text rather than the specific list block found in `ID: f8803e92e2bb` which ranked 3rd with a score of 0.2843).

### Query 3
* **Query**: Does every mismatch indicate fraud?
* **Expected Result**: Direct policy text answering if mismatches equal fraudulent activity.
* **Actual Top Result**: `ID: a5765e19fcec` (SOURCE: `data/examples/reconciliation_policy.txt`)
* **Content**: `A transaction mismatch does not automatically indicate fraud. A reconciliation system should identif`
* **Score**: 0.7377
* **Evaluation**: **Correct** (Perfect semantic match answering the prompt directly).

---

## Observations
* **Score Distribution**: Highly direct, keyword-aligned intent (Queries 1 & 3) yielded strong certainty metrics ($>0.73$). Conceptual grouping queries (Query 2) returned weaker margins ($\approx 0.45$), dropping the exact target array lower down the top-K list.
* **API Warning**: The execution pipeline triggered a HuggingFace hub rate limit warning due to a missing authentication token environment variable.

## Limitations
Current implementation:
- In-memory only.
- Linear search.
- No persistence.
- No approximate nearest-neighbor index.
- No metadata filtering.
- No hybrid search.
- No access-control filtering.

## Key Learnings
* **Token Configuration**: Exporting `HF_TOKEN` is necessary to mitigate public gateway rate-throttling during automated test builds.
* **Chunking Bottlenecks**: Truncated contents (like `identif` or `mismat`) suggest that hard character limits or lack of clean boundary tokens are trimming critical contextual vocabulary out of the vector calculations.
* **List Retrieval**: Pure dense retrieval struggles to associate broad conceptual category headers (e.g., "problems") with atomic list items when the items themselves use distinct vocabularies (e.g., "Duplicate", "Timing differences").
