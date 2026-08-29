# Sprint 4 — Day 4: Graph Retrieval

## Objective

Build a graph retrieval engine capable of resolving query entities, traversing connected knowledge, and converting retrieved subgraphs into context suitable for GraphRAG generation.

## Artifact

Graph Retrieval Engine

## Retrieval Pipeline

```text
Natural-Language Query
        ↓
Entity Resolution
        ↓
Seed Entities
        ↓
Graph Traversal
        ↓
Relevant Entities + Relationships
        ↓
Retrieved Subgraph
        ↓
Graph Context Builder
        ↓
LLM-Ready Graph Context
```

## Graph Querying vs Graph Retrieval

Graph querying provides primitive operations such as:

* Find entity
* Find neighbors
* Find incoming relationships
* Find outgoing relationships

Graph retrieval decides how those primitives should be combined to answer a user query.

The distinction is similar to the difference between a database client and a retrieval strategy.

## Seed Entities

Graph traversal requires a starting point.

For a query such as:

```text
What transactions were initiated by account ACC001?
```

the system first resolves:

```text
ACC001
```

to:

```text
account:acc001
```

This becomes a seed entity for traversal.

## Multi-Hop Traversal

A graph can retrieve connected information across multiple relationships.

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

One hop from Customer reaches Account.

Two hops reach Transaction.

Three hops reach Fraud Rule.

This makes traversal depth an important retrieval parameter.

## Breadth-First Search

Day 4 uses breadth-first search.

BFS explores entities level by level:

```text
Depth 0: Seed
Depth 1: Direct neighbors
Depth 2: Neighbors of neighbors
Depth 3: Next connected layer
```

BFS is useful when nearby graph knowledge is generally more relevant than distant knowledge.

## Cycle Protection

Enterprise graphs frequently contain cycles.

Example:

```text
Customer → Account → Transaction
    ↑                    ↓
    └────────────────────┘
```

Traversal must track visited entities to prevent infinite exploration.

## Retrieved Subgraph

The retrieval result contains more than a list of entities.

It preserves:

* Seed entities
* Retrieved entities
* Retrieved relationships
* Traversal depth
* Graph structure

This structure will later be converted into an LLM prompt.

## Graph Context

Graph context should preserve relationship semantics.

Instead of giving the LLM:

```text
Ravi Sharma
ACC001
TXN9001
```

we provide:

```text
Ravi Sharma [customer]
--owns-->
ACC001 [account]

ACC001 [account]
--initiated-->
TXN9001 [transaction]
```

The second representation preserves why the entities are related.

## Retrieval Limits

Graph traversal can expand rapidly.

A production graph retriever therefore needs controls such as:

* Maximum traversal depth
* Maximum number of entities
* Relationship filters
* Entity filters
* Ranking
* Query relevance

Day 4 implements depth and entity-count limits.

## Current Limitations

The initial entity resolver uses deterministic text matching.

It does not yet provide:

* Semantic entity matching
* Alias resolution
* Coreference resolution
* Embedding-based seed discovery
* LLM-based query understanding
* Learned graph ranking
* Path relevance scoring

These can be added without replacing the graph traversal abstraction.

## Definition of Done

* [ ] Entity-name search supported by graph query layer.
* [ ] Seed entity resolver implemented.
* [ ] Retrieval contracts implemented.
* [ ] Breadth-first graph traversal implemented.
* [ ] Multi-hop retrieval implemented.
* [ ] Cycle protection implemented.
* [ ] Traversal depth tracked.
* [ ] Maximum entity limit implemented.
* [ ] GraphRetriever implemented.
* [ ] Graph context builder implemented.
* [ ] Retrieval unit tests passing.
* [ ] Graph Retrieval Engine script executing.
* [ ] Full GraphRAG regression passing.
* [ ] Full repository regression passing.
* [ ] Report completed.
* [ ] Scoreboard updated.
* [ ] Git changes committed and merged.
