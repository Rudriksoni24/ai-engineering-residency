# Sprint 4 — Day 3: Graph Storage and Querying

## Objective

Persist knowledge graph entities and relationships locally and implement query operations over stored graph knowledge.

## Artifact

Local Knowledge Graph

## Pipeline

```text
Document
    ↓
Knowledge Extraction
    ↓
Entity Normalization
    ↓
KnowledgeGraph
    ↓
SQLiteGraphStore
    ↓
Persistent Entities + Relationships
    ↓
GraphQueryService
```

## Why Persistence Matters

The Day 1 graph existed only in memory.

When the process terminated, the graph disappeared.

A production knowledge system requires persistent storage so extracted knowledge can be reused across:

* Application restarts
* Multiple documents
* Retrieval requests
* Evaluation runs
* Graph traversal operations

## Graph Storage Model

The local graph contains two primary structures:

```text
entities
relationships
```

Entities are stored as graph nodes.

Relationships are stored as directed graph edges.

Example:

```text
customer:ravi_sharma
        |
       owns
        |
        v
account:acc001
        |
     initiated
        |
        v
transaction:txn9001
```

## Entity Storage

Each entity stores:

* Entity ID
* Entity type
* Name
* Properties

## Relationship Storage

Each relationship stores:

* Relationship ID
* Source entity ID
* Target entity ID
* Relationship type
* Properties

## Graph Queries

Day 3 implements local queries for:

* Entity lookup by ID
* Entity lookup by type
* All entities
* All relationships
* Outgoing relationships
* Incoming relationships
* Neighbor discovery
* Relationship filtering

## Storage Abstraction

Graph storage is separated from the graph domain model.

The domain layer represents knowledge.

The storage layer persists knowledge.

This allows future implementations such as:

* Neo4j
* PostgreSQL
* Memgraph
* Amazon Neptune
* Cosmos DB

without redesigning the higher-level GraphRAG pipeline.

## Why SQLite First

SQLite gives us:

* Local persistence
* Transactions
* Referential integrity
* SQL querying
* Zero additional infrastructure

The goal today is to understand persistent graph representation rather than depend on a graph database product.

## Important Limitation

SQLite is not itself a native graph database.

Multi-hop traversal is possible but becomes increasingly cumbersome compared with graph-native query languages and storage engines.

This limitation is intentional and will help demonstrate why specialized graph stores exist.

## Definition of Done

* [ ] Graph storage contract implemented.
* [ ] SQLite schema implemented.
* [ ] Entity persistence implemented.
* [ ] Relationship persistence implemented.
* [ ] Entity properties serialized safely.
* [ ] Relationship properties serialized safely.
* [ ] Entity lookup implemented.
* [ ] Entity type query implemented.
* [ ] Incoming relationship query implemented.
* [ ] Outgoing relationship query implemented.
* [ ] Neighbor query implemented.
* [ ] Graph persistence verified across store instances.
* [ ] Unit tests passing.
* [ ] Local Knowledge Graph script executing.
* [ ] Full repository regression passing.
* [ ] Report completed.
* [ ] Scoreboard updated.
* [ ] Git changes committed and merged.
