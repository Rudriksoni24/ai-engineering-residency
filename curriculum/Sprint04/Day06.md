# Sprint 4 — Day 6: Compare Vector RAG vs GraphRAG

## Objective

Compare Vector RAG and GraphRAG using equivalent banking questions and identify which retrieval architecture is appropriate for different knowledge structures.

## Artifact

Retrieval Comparison Report

## Core Question

GraphRAG is not automatically better than Vector RAG.

The appropriate retrieval architecture depends on the structure of the knowledge and the questions being asked.

## Vector RAG

Vector RAG primarily retrieves content based on semantic similarity.

```text
Query
  ↓
Embedding
  ↓
Vector Search
  ↓
Relevant Chunks
  ↓
LLM
```

It is particularly effective when the answer exists directly inside one or more semantically relevant passages.

Example:

```text
What is the daily UPI transfer limit?
```

If a document explicitly states the limit, vector retrieval can retrieve the relevant passage directly.

## GraphRAG

GraphRAG retrieves explicit entities and relationships.

```text
Query
  ↓
Entity Resolution
  ↓
Seed Entity
  ↓
Graph Traversal
  ↓
Connected Subgraph
  ↓
LLM
```

It becomes useful when answering requires connected facts.

Example:

```text
Which fraud rule flagged the transaction initiated by ACC001?
```

The answer may require:

```text
ACC001
   ↓ initiated
Transaction
   ↓ flagged_by
Fraud Rule
```

## Direct Questions

A direct factual question generally does not require graph traversal.

Examples:

* What is the minimum balance?
* What is the transfer limit?
* What documents are required?
* What are the account charges?

Vector RAG is usually simpler for these questions.

## Relationship Questions

Relationship-oriented questions ask how entities are connected.

Examples:

* Which account belongs to Ravi?
* Which transaction was initiated by ACC001?
* Which merchant received TXN001?

GraphRAG can represent these relationships explicitly.

## Multi-Hop Questions

Multi-hop questions require following several connected facts.

Example:

```text
Customer
   ↓ owns
Account
   ↓ initiated
Transaction
   ↓ flagged_by
Fraud Rule
```

GraphRAG is particularly useful when this relationship chain is important to the answer.

## Why GraphRAG Can Be Unnecessary

GraphRAG introduces additional infrastructure:

* Entity extraction
* Relationship extraction
* Entity resolution
* Graph storage
* Traversal
* Graph maintenance
* Graph retrieval ranking

If relevant answers already exist directly inside retrievable passages, this additional complexity may provide little benefit.

## Evaluation Dimensions

Day 6 compares both systems using:

* Answer keyword coverage
* Retrieval success
* Retrieved evidence count
* Relationship evidence
* Latency
* Query type

## Fair Comparison

The same query and expected answer should be passed to both systems.

The comparison layer should not know the internal database or retrieval implementation.

It interacts with each system through a shared answer contract.

## Architectural Principle

Evaluation code should depend on abstractions.

```text
RetrievalSystem
      ↑
      │
 ┌────┴────┐
 │         │
Vector   Graph
Adapter   Adapter
```

This allows retrieval systems to evolve independently from the evaluation framework.

## Expected Outcome

The goal is not to produce a winner.

The goal is to identify suitability.

Typical expectation:

```text
Direct factual retrieval
→ Vector RAG often sufficient

Explicit relationship retrieval
→ GraphRAG often advantageous

Multi-hop connected reasoning
→ GraphRAG often advantageous

Unstructured semantic knowledge
→ Vector RAG often simpler

Mixed enterprise knowledge
→ Hybrid retrieval may be strongest
```

## Definition of Done

* [ ] Common retrieval comparison contract implemented.
* [ ] Vector RAG adapter implemented.
* [ ] GraphRAG adapter implemented.
* [ ] Comparison cases implemented.
* [ ] Keyword coverage metric implemented.
* [ ] Retrieval success captured.
* [ ] Evidence counts captured.
* [ ] Relationship evidence captured.
* [ ] Latency captured.
* [ ] Comparison engine implemented.
* [ ] Unit tests passing.
* [ ] Comparison script executing.
* [ ] Retrieval Comparison Report completed.
* [ ] GraphRAG regression passing.
* [ ] Full repository regression passing.
* [ ] Scoreboard updated.
* [ ] Git changes committed and merged.
