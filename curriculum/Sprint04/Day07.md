# Sprint 4 — Day 7: Sprint Integration

## Objective

Integrate graph modeling, knowledge extraction, graph persistence, graph retrieval, and GraphRAG generation into a reusable banking intelligence application.

## Artifact

Banking Graph Intelligence System

## Final Architecture

```text
Banking Document
      ↓
Knowledge Extraction
      ↓
ExtractionGraphBuilder
      ↓
KnowledgeGraph
      ↓
GraphStore
      ↓
GraphQueryService
      ↓
EntityResolver
      ↓
GraphTraversal
      ↓
GraphRetriever
      ↓
GraphContextBuilder
      ↓
GraphRAGPromptBuilder
      ↓
TextGenerator
      ↓
BankingGraphIntelligenceService
```

## Application Layer

Previous Sprint 4 days implemented infrastructure and domain components.

Day 7 introduces an application layer responsible for coordinating those components through a banking-oriented service.

The application layer does not implement:

* SQL
* Graph traversal algorithms
* Entity extraction rules
* LLM networking

Instead, it orchestrates those capabilities.

## BankingGraphIntelligenceService

The service exposes high-level operations such as:

* Ingest banking knowledge
* Inspect known entities
* Retrieve graph context
* Answer graph-grounded questions

This gives callers one stable entry point into the GraphRAG system.

## Dependency Injection

The service receives its collaborators through its constructor.

This allows:

* Unit testing
* Fake generators
* Alternate stores
* Alternate extractors
* Future Neo4j integration
* Future hosted LLM integration

## Application Factory

Construction of the full dependency graph belongs in a factory rather than inside business logic.

Example:

```text
Factory
  ↓
SQLiteGraphStore
  ↓
GraphQueryService
  ↓
EntityResolver
  ↓
GraphTraversal
  ↓
GraphRetriever
  ↓
GraphRAGPipeline
  ↓
BankingGraphIntelligenceService
```

This keeps object wiring separate from system behavior.

## Integration Testing

Unit tests verify isolated components.

Integration tests verify that multiple real components operate together.

The final Sprint integration should demonstrate:

```text
Document
   ↓
Extraction
   ↓
Persistence
   ↓
Retrieval
   ↓
Graph Context
   ↓
Grounded Answer
```

without requiring a live Ollama model in automated tests.

A fake generator is used for deterministic test execution.

## Production Boundary

A production GraphRAG system would additionally require:

* Authentication and authorization
* Tenant isolation
* Source provenance
* Incremental graph updates
* Entity resolution
* Observability
* Retrieval metrics
* Prompt/version tracking
* Evaluation datasets
* Graph schema governance
* Backup and recovery
* Permission-aware traversal

These concerns are acknowledged but remain outside the learning scope of Sprint 4.

## Sprint Architecture Principle

GraphRAG is valuable only when graph structure provides useful information.

For direct factual document questions, Vector RAG may remain the simpler architecture.

For connected entity-centric and multi-hop questions, graph retrieval becomes more valuable.

For mixed enterprise workloads, hybrid retrieval is often appropriate.

## Sprint Exit Criteria

By completing Day 7, the Sprint should demonstrate:

* [ ] Model entities and relationships.
* [ ] Extract entities from documents.
* [ ] Build and query a knowledge graph.
* [ ] Implement graph traversal.
* [ ] Combine graph retrieval with LLM generation.
* [ ] Compare GraphRAG with Vector RAG.
* [ ] Explain when GraphRAG is unnecessary.

## Definition of Done

* [ ] Application contracts implemented.
* [ ] Banking configuration implemented.
* [ ] Banking Graph Intelligence service implemented.
* [ ] Application factory implemented.
* [ ] Document ingestion integration implemented.
* [ ] Persistent graph integration implemented.
* [ ] Graph retrieval integration implemented.
* [ ] GraphRAG answer integration implemented.
* [ ] Deterministic end-to-end integration test passing.
* [ ] Local executable application working.
* [ ] Complete GraphRAG test suite passing.
* [ ] Complete repository regression passing.
* [ ] Day 7 report completed.
* [ ] Sprint 4 review completed.
* [ ] Sprint exit criteria completed.
* [ ] Scoreboard completed.
* [ ] Git changes committed and merged.
