# Sprint 4 — Day 5 Report: GraphRAG Architecture

## Summary

Implemented the end-to-end GraphRAG Pipeline by connecting graph retrieval, structured graph context construction, prompt generation, and local LLM inference.

## Artifact

GraphRAG Pipeline

## Architecture

```text
User Query
    ↓
EntityResolver
    ↓
GraphRetriever
    ↓
GraphTraversal
    ↓
Retrieved Subgraph
    ↓
GraphContextBuilder
    ↓
GraphRAGPromptBuilder
    ↓
TextGenerator
    ↓
Local LLM
    ↓
GraphRAGResponse
```

## Components Implemented

### TextGenerator

Defines the generation abstraction required by the GraphRAG pipeline.

The pipeline therefore does not depend directly on Ollama.

### GraphRAGPromptBuilder

Constructs a grounded generation prompt containing:

* User question
* Retrieved graph context
* Grounding rules
* Anti-hallucination instructions

### OllamaGenerator

Implements local text generation through the Ollama HTTP API.

The adapter converts a plain prompt into a generated response while keeping Ollama-specific behavior outside the GraphRAG pipeline.

### GraphRAGPipeline

Coordinates:

1. Query validation
2. Graph retrieval
3. Graph context construction
4. Prompt construction
5. Language-model generation
6. Response metadata construction

### GraphRAGResponse

Returns:

* Generated answer
* Seed entity IDs
* Retrieved entity count
* Retrieved relationship count
* Graph context

## Grounding Behavior

The language model is called only when graph retrieval produces grounded context.

If no seed entity can be resolved, the pipeline returns:

```text
I don't know based on the available graph knowledge.
```

without calling the LLM.

This prevents an ungrounded GraphRAG request from silently becoming ordinary language-model generation.

## Example

Query:

```text
What transaction was initiated by ACC001?
```

Retrieved graph:

```text
Ravi Sharma [customer]
--[owns]-->
ACC001 [account]

ACC001 [account]
--[initiated]-->
TXN9001 [transaction]
```

The graph context is provided to the local model, allowing it to answer from explicit relationship evidence.

## GraphRAG vs Graph Query

A graph query returns structured entities and relationships.

GraphRAG adds:

* Query interpretation
* Retrieval orchestration
* Context construction
* Prompt generation
* Language-model answer generation

Therefore GraphRAG is an application architecture built on graph retrieval rather than simply a graph database query.

## GraphRAG vs Vector RAG

Vector RAG retrieves text based primarily on semantic similarity.

GraphRAG retrieves connected entities and relationships.

Vector RAG is effective for questions where relevant knowledge is contained in semantically similar passages.

GraphRAG becomes useful when answering questions depends on explicit relationships or multi-hop connections.

## Current Limitations

The pipeline currently uses:

* Exact entity-name resolution
* Breadth-first traversal
* Simple depth/entity limits
* Unranked graph paths
* Plain textual graph context

It does not yet implement:

* Semantic entity linking
* Hybrid vector/graph retrieval
* Path relevance scoring
* Graph community retrieval
* Context compression
* Citation formatting
* Production observability

## Validation

Day 5 unit tests:

```bash
uv run pytest \
  graphrag/tests/test_graphrag_prompt_builder.py \
  graphrag/tests/test_graphrag_pipeline.py \
  graphrag/tests/test_ollama_generator.py \
  -v
```

Complete GraphRAG tests:

```bash
uv run pytest graphrag/tests -v
```

Real local GraphRAG:

```bash
uv run python -m graphrag.scripts.run_graphrag
```

Complete repository regression:

```bash
uv run pytest -v
```

## Key Learning

GraphRAG is not simply a graph database connected to an LLM.

A complete GraphRAG system requires:

* Entity resolution
* Retrieval strategy
* Traversal policy
* Retrieval limits
* Subgraph construction
* Context serialization
* Prompt grounding
* Generation orchestration

The quality of retrieval remains as important as the quality of the language model.

## Next Step

Sprint 4 Day 6 will compare Vector RAG and GraphRAG using equivalent banking questions and analyze where each retrieval strategy succeeds or fails.
