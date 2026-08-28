# Sprint 3 — Day 7: Evaluation Dataset & RAG Benchmark

## Objective

Build a repeatable evaluation dataset and benchmark framework for the local RAG system.

## Concepts

* Evaluation datasets
* Benchmarking
* Test cases
* Expected answers
* Aggregate scores
* Repeatable evaluation
* Regression testing for RAG systems

## Architecture

```text
Evaluation Dataset
        │
        ▼
EvaluationDataset
        │
        ▼
RAGBenchmark
        │
        ├── RAG Pipeline
        │
        └── RAGEvaluator
                │
                ▼
        Evaluation Results
                │
                ▼
          BenchmarkResult
```

## Key Learning

A single successful RAG response does not demonstrate system quality.

A benchmark allows the same set of questions to be executed repeatedly as the retrieval system, embeddings, prompts, or models change.

This creates the foundation for regression evaluation.

## Deliverables

* JSON evaluation dataset
* Dataset loader
* Benchmark runner
* Aggregate benchmark result
* Dataset tests
* Benchmark tests
* Benchmark execution script

## Exit Criteria

* Load an evaluation dataset.
* Execute multiple evaluation cases.
* Aggregate evaluation results.
* Explain why benchmark datasets are necessary.
* Explain the difference between unit tests and RAG evaluation benchmarks.
* Identify limitations in the current benchmark design.
