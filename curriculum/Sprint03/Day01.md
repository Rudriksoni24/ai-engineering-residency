# Sprint 3 — Day 1

# RAG Foundations and Document Ingestion

## Goal

Build a clean document ingestion foundation for a local RAG system.

## Learning Objectives

By the end of this day, I should understand:

- What RAG actually solves.
- The difference between ingestion and retrieval.
- Why documents need normalized contracts.
- Why metadata is important.
- Why loaders should be isolated.
- Why raw documents should not directly enter an embedding pipeline.

## Architecture

Document
    ↓
Loader
    ↓
Raw Content
    ↓
Normalizer
    ↓
Document Contract
    ↓
Future Chunking Pipeline

## Deliverables

- [ ] RAG package created.
- [ ] Document contract created.
- [ ] Base loader abstraction created.
- [ ] Text loader implemented.
- [ ] Document normalization implemented.
- [ ] Metadata preserved.
- [ ] Unit tests created.
- [ ] Sample ingestion executed.
- [ ] Report completed.

## Definition of Done

- [ ] Text document loads successfully.
- [ ] Empty document is rejected.
- [ ] Metadata is preserved.
- [ ] Whitespace is normalized.
- [ ] Tests pass.
- [ ] Ruff passes.