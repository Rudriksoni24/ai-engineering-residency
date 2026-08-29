# Sprint 4 — Day 2: Entity and Relationship Extraction

## Objective

Build a knowledge extraction pipeline that converts unstructured enterprise text into graph entities and relationships.

## Artifact

Knowledge Extraction Pipeline

## Pipeline

```text
Document
    ↓
Knowledge Extractor
    ↓
Extracted Entities
    +
Extracted Relationships
    ↓
Normalization
    ↓
Graph Builder
    ↓
Knowledge Graph
```

## Extracted Knowledge

Extracted entities and relationships are intentionally separate from the final graph models.

An extracted entity represents a candidate concept discovered in source text.

Example:

```text
Customer Ravi Sharma
```

may produce:

```text
name = Ravi Sharma
entity_type = customer
```

The graph layer later assigns a stable identifier:

```text
customer:ravi_sharma
```

## Entity Normalization

Entity normalization makes graph identifiers deterministic.

Example:

```text
Customer
CUSTOMER
customer
```

all normalize to:

```text
customer
```

Likewise:

```text
Ravi Sharma
```

becomes:

```text
customer:ravi_sharma
```

## Relationship Extraction

Relationships encode how entities interact.

Example source:

```text
Customer Ravi Sharma owns account ACC001.
```

Extracted relationship:

```text
Ravi Sharma --owns--> ACC001
```

Graph relationship:

```text
customer:ravi_sharma
    --owns-->
account:acc001
```

## Why Extraction and Graph Modeling Are Separate

Extraction is probabilistic or heuristic.

Graph modeling requires stable identifiers and validated relationships.

Keeping these concerns separate allows the extraction strategy to change without redesigning the graph domain model.

Future extraction mechanisms could include:

* Rules
* Named Entity Recognition
* Transformer models
* Local LLM structured output
* Hybrid pipelines

The downstream graph system can remain unchanged.

## Implementation

Day 2 implements:

* Extraction contracts
* Entity normalization
* Stable entity IDs
* Stable relationship IDs
* Banking knowledge extractor
* Relationship extraction
* Extraction-to-graph conversion
* Unit tests
* Executable extraction pipeline

## Current Limitations

The Day 2 extractor is deterministic and intentionally narrow.

It does not yet support:

* Pronoun resolution
* Entity aliases
* Coreference resolution
* Complex sentence structures
* Multiple entities of the same type in one relationship clause
* LLM-based extraction
* Confidence scores
* Source provenance

These limitations are intentional and establish the baseline for more advanced extraction.

## Definition of Done

* [ ] Extraction contracts implemented.
* [ ] Entity validation implemented.
* [ ] Relationship validation implemented.
* [ ] Entity normalization implemented.
* [ ] Stable entity IDs generated.
* [ ] Stable relationship IDs generated.
* [ ] Customer extraction implemented.
* [ ] Account extraction implemented.
* [ ] Transaction extraction implemented.
* [ ] Relationship extraction implemented.
* [ ] Extraction graph builder implemented.
* [ ] Unit tests passing.
* [ ] Knowledge extraction script executing.
* [ ] Full regression tests passing.
* [ ] Report completed.
* [ ] Scoreboard updated.
* [ ] Git changes committed and merged.
