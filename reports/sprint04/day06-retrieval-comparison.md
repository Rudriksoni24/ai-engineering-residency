# Sprint 4 — Day 6 Report: Vector RAG vs GraphRAG

## Summary

Compared the Vector RAG system built during Sprint 3 with the GraphRAG system built during Sprint 4.

The objective was not to identify a universally superior retrieval architecture. The objective was to understand how retrieval architecture should match the structure of enterprise knowledge and user questions.

## Artifact

Retrieval Comparison Report

## Systems Compared

### Vector RAG

```text
Query
  ↓
Semantic Retrieval
  ↓
Relevant Chunks
  ↓
Prompt
  ↓
LLM
```

### GraphRAG

```text
Query
  ↓
Entity Resolution
  ↓
Graph Traversal
  ↓
Relevant Subgraph
  ↓
Graph Context
  ↓
Prompt
  ↓
LLM
```

## Evaluation Dimensions

The systems were compared using:

* Retrieval success
* Expected-answer keyword coverage
* Retrieved evidence count
* Retrieved graph relationship count
* Observed latency
* Query type

Latency measurements are observational and should not be interpreted as a formal production benchmark.

## Experimental Results

Insert the actual results produced by:

```bash
uv run python -m graphrag.scripts.run_retrieval_comparison
```

Do not fabricate values.

Suggested table:

| Case       | Type         | Vector Coverage | Graph Coverage | Vector Evidence | Graph Evidence | Graph Relationships |
| ---------- | ------------ | --------------: | -------------: | --------------: | -------------: | ------------------: |
| direct-001 | Relationship |            0.00 |           0.33 |               3 |              3 |                   2 |
| entity-001 | Relationship |            0.00 |           0.25 |               3 |              3 |                   2 |

## Direct Factual Retrieval

Vector RAG is generally well suited when the answer exists directly in a semantically retrievable passage.

Examples include:

* Account limits
* Product descriptions
* Policy statements
* Fees
* Procedures
* Documentation requirements

Creating and maintaining a graph for these questions may add complexity without improving the answer.

## Relationship Retrieval

GraphRAG becomes valuable when explicit connections between entities are important.

Example:

```text
Ravi Sharma
    ↓ owns
ACC001
    ↓ initiated
TXN9001
```

The graph represents the relationships explicitly rather than relying on the relevant statements appearing together in retrieved text.

## Multi-Hop Retrieval

GraphRAG becomes increasingly attractive when answering a question requires following several connected relationships.

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

This relationship chain maps naturally to graph traversal.

## Vector RAG Advantages

Vector RAG provides:

* Simpler ingestion
* Natural support for unstructured text
* Semantic matching
* Lower modeling overhead
* Fewer entity-resolution requirements

It is often the appropriate default for document-oriented knowledge systems.

## GraphRAG Advantages

GraphRAG provides:

* Explicit relationships
* Multi-hop traversal
* Structured evidence
* Relationship-aware context
* Better representation of connected enterprise knowledge

## GraphRAG Costs

GraphRAG requires additional engineering for:

* Entity extraction
* Relationship extraction
* Entity resolution
* Graph storage
* Graph updates
* Traversal policies
* Relevance control

These costs should be justified by the use case.

## When GraphRAG Is Unnecessary

GraphRAG is generally unnecessary when:

* Questions are direct factual lookups.
* Relevant answers already occur inside retrievable passages.
* Relationships are not important to answering the question.
* The knowledge base is mostly independent documents.
* Graph construction and maintenance would exceed the retrieval benefit.

## When GraphRAG Is Appropriate

GraphRAG is appropriate when:

* The domain contains strongly connected entities.
* Relationship semantics matter.
* Questions frequently require several hops.
* Structured provenance is valuable.
* Entity-centric exploration is required.

## Hybrid Architecture

Vector and graph retrieval are complementary.

A mature enterprise system may use:

```text
Query
  ↓
Query Routing
  ├── Vector Retrieval
  └── Graph Retrieval
            ↓
       Combined Evidence
            ↓
         Reranking
            ↓
            LLM
```

Vector retrieval handles semantic document knowledge.

Graph retrieval handles connected relational knowledge.

## Conclusion

GraphRAG should not replace Vector RAG simply because graph retrieval is more sophisticated.

Retrieval architecture should be selected according to the structure of the knowledge and the reasoning required by user queries.

For document-centric factual retrieval, Vector RAG is often sufficient and simpler.

For connected entity-centric and multi-hop retrieval, GraphRAG can provide substantially better structure.

For complex enterprise systems containing both types of knowledge, hybrid retrieval is a strong architectural direction.

## Next Step

Sprint 4 Day 7 will integrate the graph extraction, storage, retrieval, and generation layers into the Banking Graph Intelligence System.
