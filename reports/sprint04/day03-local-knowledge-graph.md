# Sprint 4 — Day 3 Report: Graph Storage and Querying

## Summary

Implemented persistent local graph storage and graph query capabilities for the GraphRAG system.

The knowledge graph created from extracted banking documents can now survive application restarts and be queried through a storage-independent service layer.

## Artifact

Local Knowledge Graph

## Architecture

```text
Knowledge Extraction
        ↓
KnowledgeGraph
        ↓
SQLiteGraphStore
        ↓
SQLite Database
        ↓
GraphQueryService
```

## Components Implemented

### GraphStore

Defines the persistence interface required by higher-level GraphRAG components.

The abstraction prevents the application from becoming directly coupled to SQLite.

### SQLiteGraphStore

Provides persistent storage for:

* Entities
* Relationships
* Entity properties
* Relationship properties

The implementation includes indexes for:

* Entity type
* Relationship source
* Relationship target
* Relationship type

### GraphQueryService

Provides higher-level graph queries without exposing SQL to GraphRAG consumers.

Supported operations include:

* Entity lookup
* Entity type filtering
* Neighbor discovery
* Incoming relationships
* Outgoing relationships
* Relationship type filtering

## Persistent Banking Graph

The Day 2 extraction pipeline is connected to the Day 3 graph store.

Example:

```text
Customer Ravi Sharma owns account ACC001.
Account ACC001 initiated transaction TXN9001.
```

becomes:

```text
customer:ravi_sharma
        |
       owns
        v
account:acc001
        |
    initiated
        v
transaction:txn9001
```

and is persisted inside:

```text
data/graphrag/banking_knowledge.db
```

## Persistence Validation

The graph is loaded into one SQLite store instance and successfully retrieved from subsequent store instances.

Repeated execution does not duplicate entities or relationships because stable identifiers and upsert behavior are used.

## Storage Design

Entities are stored as nodes.

Relationships are stored as directed edges.

Properties are serialized as JSON.

Foreign-key constraints prevent relationships from referencing nonexistent entities.

## Why SQLite

SQLite was selected for the first persistent implementation because it provides:

* Persistence
* Transactions
* Referential integrity
* Local querying
* Zero external infrastructure

It also exposes the limitations of relational storage for complex graph traversal, making the motivation for graph-native databases easier to understand.

## Limitations

The current implementation does not yet provide:

* Recursive multi-hop traversal
* Shortest path queries
* Path scoring
* Graph retrieval ranking
* Cypher queries
* Distributed graph storage
* Entity resolution
* Graph embeddings

These are intentionally outside Day 3.

## Validation

Day 3 tests:

```bash
uv run pytest \
  graphrag/tests/test_sqlite_graph_store.py \
  graphrag/tests/test_graph_query_service.py \
  -v
```

Complete GraphRAG suite:

```bash
uv run pytest graphrag/tests -v
```

Local Knowledge Graph:

```bash
uv run python -m graphrag.scripts.run_local_knowledge_graph
```

Full regression:

```bash
uv run pytest -v
```

## Key Learning

A graph model and a graph database are different concerns.

The domain model describes connected knowledge.

The storage implementation determines how that knowledge is persisted and queried.

Separating these concerns allows GraphRAG retrieval to remain independent of the underlying database technology.

## Next Step

Sprint 4 Day 4 will build the Graph Retrieval Engine, including traversal across connected entities and retrieval of relevant graph context.
