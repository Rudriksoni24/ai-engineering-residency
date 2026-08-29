# Sprint 4 — Day 2 Report: Entity and Relationship Extraction

## Summary

Implemented the initial knowledge extraction pipeline for GraphRAG.

The system can convert structured banking statements into extracted entities and relationships and then transform those results into the knowledge graph model created during Day 1.

## Artifact

Knowledge Extraction Pipeline

## Components Implemented

### ExtractedEntity

Represents a candidate entity discovered in source text.

Contains:

* Name
* Entity type
* Properties

### ExtractedRelationship

Represents a candidate relationship discovered between two extracted entities.

Contains:

* Source name
* Target name
* Relationship type
* Properties

### KnowledgeExtractionResult

Groups extracted entities and relationships into one immutable extraction result.

### EntityNormalizer

Provides deterministic normalization for:

* Entity names
* Entity types
* Entity identifiers
* Relationship identifiers

### BankingKnowledgeExtractor

Extracts initial banking concepts from textual statements.

Supported entities currently include:

* Customer
* Account
* Transaction

Supported relationships include:

* owns
* initiated

### ExtractionGraphBuilder

Converts extraction results into the Day 1 knowledge graph domain model.

This provides the bridge between unstructured source content and structured graph knowledge.

## Example

Input:

```text
Customer Ravi Sharma owns account ACC001.
Account ACC001 initiated transaction TXN9001.
```

Extracted knowledge:

```text
Ravi Sharma [customer]
ACC001 [account]
TXN9001 [transaction]

Ravi Sharma --owns--> ACC001
ACC001 --initiated--> TXN9001
```

Graph representation:

```text
customer:ravi_sharma
    --owns-->
account:acc001
    --initiated-->
transaction:txn9001
```

## Architectural Learning

Extraction and graph modeling should remain separate.

The extraction layer identifies candidate knowledge.

The normalization and graph-building layers convert that knowledge into stable graph structures.

This means a future LLM-based extractor can replace the rule-based implementation without changing the graph domain model.

## Validation

Day 2 tests are executed using:

```bash
uv run pytest \
  graphrag/tests/test_extraction_contracts.py \
  graphrag/tests/test_entity_normalizer.py \
  graphrag/tests/test_knowledge_extractor.py \
  graphrag/tests/test_extraction_graph_builder.py \
  -v
```

The complete GraphRAG suite is executed using:

```bash
uv run pytest graphrag/tests -v
```

The executable knowledge extraction pipeline is run using:

```bash
uv run python -m graphrag.scripts.run_knowledge_extraction
```

## Current Limitations

The current extractor uses deterministic rules and supports a deliberately small banking vocabulary.

It does not yet solve:

* Entity disambiguation
* Coreference
* Aliases
* Confidence scoring
* Complex entity extraction
* LLM-based structured extraction
* Source provenance

These will become important as the graph becomes production-oriented.

## Next Step

Sprint 4 Day 3 will persist and query the extracted graph through the Local Knowledge Graph layer.
