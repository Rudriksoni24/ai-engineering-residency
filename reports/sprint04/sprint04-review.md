# Sprint 4 Review — GraphRAG

## Target

Build a graph-based retrieval system for connected enterprise knowledge.

## Completed Artifacts

| Day   | Topic                              | Artifact                          |
| ----- | ---------------------------------- | --------------------------------- |
| Day 1 | Knowledge Graph Fundamentals       | Graph Modeling Lab                |
| Day 2 | Entity and Relationship Extraction | Knowledge Extraction Pipeline     |
| Day 3 | Graph Storage and Querying         | Local Knowledge Graph             |
| Day 4 | Graph Retrieval                    | Graph Retrieval Engine            |
| Day 5 | GraphRAG Architecture              | GraphRAG Pipeline                 |
| Day 6 | Compare Vector RAG vs GraphRAG     | Retrieval Comparison Report       |
| Day 7 | Sprint Integration                 | Banking Graph Intelligence System |

## Final Capabilities

Sprint 4 implements:

* Graph entities
* Directed relationships
* Graph properties
* Entity and relationship extraction
* Entity normalization
* Stable graph IDs
* Persistent graph storage
* Entity queries
* Relationship queries
* Neighbor discovery
* Breadth-first traversal
* Multi-hop traversal
* Cycle protection
* Retrieval limits
* Entity resolution
* Graph context construction
* GraphRAG prompting
* Local LLM generation
* Vector RAG versus GraphRAG comparison
* Banking Graph Intelligence integration

## Sprint Exit Criteria

* [x] Model entities and relationships.
* [x] Extract entities from documents.
* [x] Build and query a knowledge graph.
* [x] Implement graph traversal.
* [x] Combine graph retrieval with LLM generation.
* [x] Compare GraphRAG with Vector RAG.
* [x] Explain when GraphRAG is unnecessary.

## Architecture Developed

```text
Document
   ↓
Knowledge Extraction
   ↓
Knowledge Graph
   ↓
Persistent Storage
   ↓
Entity Resolution
   ↓
Graph Retrieval
   ↓
Relevant Subgraph
   ↓
Graph Context
   ↓
Prompt
   ↓
LLM
   ↓
Grounded Answer
```

## Vector RAG vs GraphRAG

### Prefer Vector RAG When

* Knowledge is primarily unstructured documents.
* Answers exist directly in retrievable passages.
* Questions are semantic or factual.
* Graph relationships provide little additional value.
* Simpler infrastructure is desirable.

### Prefer GraphRAG When

* Entities are strongly connected.
* Relationship semantics matter.
* Queries require multiple hops.
* Entity-centric exploration is required.
* Structured graph evidence is useful.

### Consider Hybrid Retrieval When

The enterprise knowledge base contains both unstructured text and connected entities.

## Main Technical Limitations

The current system intentionally uses simplified implementations for:

* Entity resolution
* Entity extraction
* Relationship extraction
* Traversal ranking
* Context ranking
* Graph schema governance

These are the primary areas that would require improvement before production deployment.

## Main Engineering Lesson

GraphRAG is not simply a more advanced version of Vector RAG.

It solves a different retrieval problem.

The complexity of maintaining a knowledge graph is justified only when connected knowledge materially improves retrieval quality.

## Sprint Status

Sprint 4 — GraphRAG: COMPLETE.

# Final System Archetecture

                         BANKING DATA
                              │
                              ▼
                 BankingKnowledgeExtractor
                              │
                              ▼
                  KnowledgeExtractionResult
                              │
                              ▼
                  ExtractionGraphBuilder
                              │
                              ▼
                      KnowledgeGraph
                              │
                              ▼
                    SQLiteGraphStore
                              │
                              ▼
                   GraphQueryService
                              │
                              ▼
                      EntityResolver
                              │
                              ▼
                     GraphTraversal
                              │
                              ▼
                      GraphRetriever
                              │
                              ▼
                   GraphContextBuilder
                              │
                              ▼
                 GraphRAGPromptBuilder
                              │
                              ▼
                       TextGenerator
                              │
                              ▼
                    GraphRAGPipeline
                              │
                              ▼
          BankingGraphIntelligenceService


