# Sprint 3 — Day 6: RAG Evaluation & Quality

## Objective

Build a deterministic evaluation layer for the local RAG system.

The objective is to evaluate more than whether the system returns a response. The evaluation layer measures whether the generated answer overlaps with an expected answer and whether the generated answer is supported by retrieved context.

## Concepts

* Evaluation dataset
* Evaluation case
* Evaluation metrics
* Answer quality
* Context support
* Deterministic heuristics
* Metric aggregation

## Architecture

```text
RAG Output
    │
    ▼
EvaluationCase
    │
    ├── Query
    ├── Expected Answer
    ├── Retrieved Documents
    └── Generated Answer
    │
    ▼
RAGEvaluator
    │
    ├── Keyword Recall
    └── Context Coverage
    │
    ▼
EvaluationResult
```

## Metrics

### Keyword Recall

Measures the proportion of tokens from the expected answer that also appear in the generated answer.

This metric is deterministic but does not understand semantic equivalence.

### Context Coverage

Measures the proportion of generated answer tokens that appear in the retrieved context.

This acts as a basic heuristic for determining whether an answer is grounded in retrieved information.

## Key Limitation

Token overlap is not equivalent to semantic correctness.

A semantically correct answer can receive a poor score if it uses different wording. Likewise, a high lexical overlap does not guarantee factual correctness.

This implementation provides a deterministic baseline that can later be extended with embedding-based or LLM-based evaluation.

## Deliverables

* Evaluation contracts
* Keyword recall metric
* Context coverage metric
* RAG evaluator
* Unit tests
* Evaluation example

## Exit Criteria

* Explain the difference between answer quality and retrieval quality.
* Explain why keyword overlap is insufficient for semantic evaluation.
* Explain how context coverage approximates grounding.
* Run deterministic evaluation against a RAG output.
* Identify the limitations of heuristic evaluation.
