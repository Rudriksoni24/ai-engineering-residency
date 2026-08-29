# Sprint 4 — Day 1: Knowledge Graph Fundamentals

## Objective

Understand and implement the fundamental data structures behind a knowledge graph.

## Artifact

Graph Modeling Lab

## Concepts

* Knowledge graphs
* Entities
* Relationships
* Nodes and edges
* Entity properties
* Relationship properties
* Directed relationships
* Graph neighbors
* Graph traversal foundations

## Graph Model

A graph can be represented as:

G = (V, E)

Where:

* V represents vertices or entities.
* E represents edges or relationships.

A knowledge graph adds semantic meaning to those graph structures.

Example:

```text
Customer
    │
   OWNS
    ▼
Account
    │
 INITIATED
    ▼
Transaction
```

The edges describe how entities are connected rather than merely indicating similarity.

## Entity

An entity represents a concrete concept in the knowledge domain.

Examples:

* Customer
* Account
* Transaction
* Merchant
* Payment System
* Fraud Rule
* Regulation

Each entity has:

* Stable identifier
* Entity type
* Human-readable name
* Optional properties

## Relationship

A relationship connects two entities.

Example:

```text
Customer --OWNS--> Account
```

A relationship contains:

* Relationship identifier
* Source entity
* Target entity
* Relationship type
* Optional properties

## Vector Retrieval vs Graph Retrieval

Vector retrieval primarily answers:

> Which pieces of content are semantically similar to this query?

Graph retrieval can answer:

> Which entities are connected to this entity, and how are they connected?

These approaches solve different retrieval problems and can also be combined.

## Implementation

The Graph Modeling Lab implements:

* Entity domain model
* Relationship domain model
* In-memory knowledge graph
* Entity validation
* Relationship validation
* Neighbor discovery
* Incoming relationship lookup
* Outgoing relationship lookup

## Banking Graph Example

```text
Customer
    │
   owns
    ▼
Account
    │
 initiated
    ▼
Transaction
   │       │
processed  flagged
   by       by
   │         │
   ▼         ▼
  UPI    Fraud Rule
```

## Key Learning

Knowledge graphs encode relationships explicitly.

Semantic similarity alone cannot reliably represent multi-hop relationships such as:

```text
Customer
→ Account
→ Transaction
→ Fraud Rule
```

Graph structures make those connections directly queryable.

## Definition of Done

* [ ] Entity model implemented.
* [ ] Relationship model implemented.
* [ ] KnowledgeGraph implemented.
* [ ] Duplicate entities rejected.
* [ ] Invalid relationships rejected.
* [ ] Neighbor lookup implemented.
* [ ] Incoming relationship lookup implemented.
* [ ] Outgoing relationship lookup implemented.
* [ ] Banking graph modeled.
* [ ] Unit tests passing.
* [ ] Graph modeling script executing.
* [ ] Report completed.
* [ ] Scoreboard updated.
* [ ] Git changes committed and merged.
