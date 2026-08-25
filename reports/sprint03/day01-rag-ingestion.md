# Sprint 3 Day 1 — RAG Foundations and Document Ingestion

## Objective

Build a normalized document ingestion layer for a local RAG system.

## Architecture

Document Source
    ↓
Loader
    ↓
Document Contract
    ↓
Normalizer
    ↓
Future Chunking Pipeline

## Experiment

### Input

Reconciliation policy document.

### Metadata

```
{'filename': 'reconciliation_policy.txt', 'extension': '.txt'}
```

The normalizer captures only the filename and extension at this stage — no path, size, timestamps, or content hash yet. That's fine for a single local `.txt` file, but it's the first thing worth expanding once the loader set grows (see Key Learnings).

### Normalization Result

**Source:**
```
data/examples/reconciliation_policy.txt
```

**Content:**
```
Transaction reconciliation compares records between multiple financial systems. A transaction mismatch does not automatically indicate fraud. A reconciliation system should identify: - Missing transactions - Duplicate transactions - Amount mismatches - Currency mismatches - Timing differences Every automated decision should preserve evidence for audit and investigation.
```

The loader/normalizer pair correctly round-tripped the file as a single flattened block of text — the original document's line breaks and the `-` bullet markers collapsed into one continuous string. That's expected behavior for a plain-text normalizer with no structure-awareness yet, but it's worth flagging: the five bullet items (missing transactions, duplicate transactions, amount mismatches, currency mismatches, timing differences) are now indistinguishable from prose in the normalized content. A future chunker that tries to split on semantic boundaries will need either the original structure preserved upstream, or a normalization step that keeps list items delimited.

## Design Decisions

### Why use a document contract?

A document contract gives every stage after the loader a single, predictable shape to work against — `source`, `metadata`, `content` — regardless of whether the original document was a `.txt` file, a PDF, or a web page. Without it, the normalizer (and later the chunker) would need to know the quirks of every loader type. With it, loaders only have one job — get raw content out of a source and shape it into the contract — and everything downstream can be written once, against the contract, instead of once per source type.

### Why separate loading and normalization?

Loading and normalization are different kinds of work with different failure modes. Loading is an I/O concern: opening a file, hitting an API, parsing a PDF — it varies a lot by source type. Normalization is a transformation concern: cleaning whitespace, standardizing encoding, enforcing a consistent structure — and it should behave the same way no matter which loader produced the input. Keeping them separate means a new loader (say, a PDF loader) doesn't need to reimplement cleaning logic, and a change to normalization rules doesn't require touching every loader. It also makes both pieces easier to unit test in isolation.

### Why preserve metadata?

Metadata is what lets you trace a retrieved chunk back to where it came from — file path, source type, and (eventually) things like page number or section heading. In a RAG system, that traceability is what makes citations possible and makes debugging retrieval issues tractable ("why did this chunk get retrieved, and where did it come from?"). If metadata gets dropped during normalization, that link is severed permanently — there's no way to recover it later once you're several stages downstream in the chunking or embedding pipeline. The current metadata (filename + extension) is minimal but already demonstrates the pattern working end-to-end.

## Failure Cases

- Missing document
- Empty document
- Invalid encoding (future)

## Key Learnings

- The pipeline works end-to-end for the simplest case: a plain-text file loads, normalizes, and preserves both source path and metadata correctly.
- Metadata is currently thin (filename, extension only). Before chunking depends on it, consider adding things like absolute path, file size, and a content hash — useful for dedup and cache invalidation later.
- Flattening the document into one string loses the original list structure (the five bullet items in the reconciliation content are now just inline text separated by hyphens). Decide now whether structure preservation belongs in the loader, the normalizer, or is deferred entirely to the chunker — this shapes how much rework the chunking stage will need.
- Running the script as a module (`uv run python -m rag.scripts.run_ingestion`) rather than directly, and adding `pythonpath = ["."]` to `pyproject.toml` for pytest, were both required before either the script or the test suite could resolve the `rag` package — worth documenting in project setup notes so this doesn't get rediscovered next sprint.