# Sprint 3 Day 2 — Chunking Strategies

## Objective

Build and evaluate a configurable chunking engine.

---

# Architecture

Normalized Document
        ↓
Chunking Configuration
        ↓
Fixed Size Chunker
        ↓
Chunks
        ↓
Future Embedding Pipeline

---

# Test Document

Source: `reconciliation_policy.txt`, 372 characters total (verified by direct count). All four configurations below were run against this same document, so chunk count differences are purely a function of `chunk_size` and `chunk_overlap`.

---

# Configuration Experiments

## Baseline — chunk_size=100, overlap=20

Result: **5 chunks**, step size 80 (`chunk_size - overlap`), starting at offsets 0, 80, 160, 240, 320. The final chunk is a natural short remainder (52 characters) since 372 isn't evenly divisible by the step.

Observations:

The chunk starting at offset 160 cuts the word "system" down to "ystem" (chunk content begins `ystem should identify: ...`). This is a direct, observed instance of the "can split words" limitation — not theoretical, it happened on the very first config tested. The five bulleted policy items (missing/duplicate/amount/currency/timing mismatches) each land inside different chunks rather than staying together as one retrievable unit.

---

## Experiment A — Small Chunks

Configuration:

- Chunk size: 50
- Overlap: 10

Result: **10 chunks**, step size 40, offsets 0 through 360.

Observations:

Word-splitting is worse and more frequent at this size, as expected — the same offset-160 boundary reproduces the "system" → "ystem" split seen in the baseline, and additional splits appear elsewhere (`indicate` → `indi`, `Duplicate` → `Du`). Ten separate chunk IDs now exist for content that fits in roughly 3–4 sentences, which means more metadata overhead and more redundant overlapping text relative to the actual information content of each chunk — low fragmentation tolerance, low context per chunk.

---

## Experiment B — Medium Chunks

Configuration:

- Chunk size: 150
- Overlap: 30

Result: **4 chunks**, but this is the interesting one — the chunk math reveals a real bug, not just an expected trade-off.

Step size is 120, giving offsets 0, 120, 240, 360. The chunk at offset 240 already runs to the end of the document (240–372, since 240 + 150 > 372). But because the loop only checks whether the *start* offset (360) is still less than the document length, it generates one more chunk at offset 360 anyway — `"vestigation."` — which is entirely redundant: every character in it was already included in the previous chunk's tail. This is a genuine implementation gap, not a case of "large overlap creates redundancy by design" — it's producing a whole extra chunk (and chunk ID) that adds zero new information.

Observations:

Aside from that bug, the three substantive chunks here preserve noticeably more sentence-level context than either Experiment A or the baseline — e.g., the full policy definition sentence stays intact in chunk 0. But the fix (stop advancing once a chunk has already reached the document end, rather than only checking the start offset against the length) should be applied before this chunker is trusted on larger documents, since the same condition will recur any time `chunk_size` and `chunk_overlap` don't evenly divide the remaining tail.

---

## Experiment C — Large Chunks

Configuration:

- Chunk size: 500
- Overlap: 50

Result: **1 chunk** — the entire 372-character document, unsplit.

Observations:

This config doesn't actually test large-chunk trade-offs on this document, because `chunk_size` (500) exceeds the document length (372) — there's nothing to split. Zero fragmentation here is a property of the test document being smaller than the configured chunk size, not evidence that a 500-character chunk size handles fragmentation well on real documents. To properly evaluate "large chunk" behavior, this needs to be re-run against a document meaningfully longer than 500 characters (or 500 tokens, depending on what unit is eventually adopted).

---

# Comparison

| Strategy | Chunk Count | Context | Fragmentation |
|---|---:|---|---|
| Baseline (100/20) | 5 | Medium | Medium — clean word split observed |
| Small (50/10) | 10 | Low | High — multiple word splits, high ID overhead |
| Medium (150/30) | 4 (1 redundant) | Medium-High | Medium — plus a duplicate-content bug |
| Large (500/50) | 1 | High | Not exercised — document smaller than chunk size |

---

# Design Decisions

## Why configurable chunking?

Different downstream needs — embedding model context limits, retrieval granularity, index size — pull chunk size in different directions, and no single fixed size serves all of them well. Making `chunk_size` and `chunk_overlap` configuration rather than hardcoded constants is what made it possible to run this exact experiment: four configs against the same document, with nothing but config values changing, to see the fragmentation/context trade-off directly instead of guessing at it.

## Why preserve metadata?

Same reasoning as the ingestion stage: metadata is the only thing that lets a retrieved chunk be traced back to its source document. At the chunking stage specifically, it also has to carry the chunk's own position (`chunk_index`) so that adjacent chunks can be reassembled or referenced in order — without that, there's no way to tell whether two retrieved chunks are neighbors or from unrelated parts of the document.

## Why generate stable chunk IDs?

Stable, content-derived chunk IDs make ingestion idempotent — re-running the pipeline on an unchanged document should produce the same IDs rather than new ones, so a downstream vector store can detect "this chunk already exists" instead of silently duplicating it on every re-run. This hasn't been explicitly verified yet in this experiment (each config was only run once), so it's worth a follow-up test: run the same config twice and confirm the resulting chunk IDs match exactly.

---

# Limitations

The current implementation:

- Can split words — directly observed (`system` → `ystem` at the offset-160 boundary in two different configs).
- Can split sentences.
- Does not understand document sections.
- Does not use tokens — chunking is character-based, so `chunk_size=100` means 100 characters, not 100 tokens, which is what an embedding model actually cares about.
- Does not understand semantic boundaries.
- Has a boundary bug where it can emit a redundant final chunk whose content is entirely already covered by the previous chunk, observed concretely in the 150/30 configuration.

---

# Key Learnings

- The word-splitting limitation isn't theoretical — it reproduced identically at the same document offset (160) across two different configs (100/20 and 50/10), confirming it's a structural property of character-based fixed splitting, not a one-off.
- The 150/30 run surfaced a real bug: the chunker can generate a fully redundant trailing chunk when the step size doesn't evenly divide into the remaining document tail. Fix before scaling up — check whether the previous chunk already reached the document end before advancing to a new start offset.
- The "Large Chunks" experiment didn't actually test large-chunk behavior, since the document (372 characters) was smaller than the configured chunk size (500). Re-run this config against a longer document to get a meaningful read on large-chunk fragmentation trade-offs.
- Chunk ID stability across repeated runs of the same config hasn't been verified yet — worth a quick test (run once, run again, diff the IDs) before relying on IDs for dedup in a real vector store.
- Moving to token-based chunk sizing (rather than raw character counts) is the natural next step, since embedding models have token limits, not character limits — a 500-character chunk and a 500-token chunk behave very differently.