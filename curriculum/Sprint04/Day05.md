# Sprint 4 — Day 5: GraphRAG Architecture

## Objective

Combine graph retrieval with local language-model generation to create an end-to-end GraphRAG pipeline.

## Artifact

GraphRAG Pipeline

## Architecture

```text
User Query
    ↓
Entity Resolution
    ↓
Seed Entities
    ↓
Graph Traversal
    ↓
Retrieved Subgraph
    ↓
Graph Context Builder
    ↓
GraphRAG Prompt
    ↓
Local LLM
    ↓
Grounded Answer
```

## What Makes This GraphRAG?

A standard RAG system typically retrieves semantically similar text chunks.

GraphRAG retrieves structured connected knowledge.

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

The graph provides explicit relationship semantics that can be preserved in the generation context.

## Retrieval and Generation Are Separate

The retriever is responsible for finding relevant knowledge.

The generator is responsible for producing an answer from supplied context.

The pipeline orchestrates both.

This separation is important because retrieval can be tested independently from LLM generation.

## Generator Abstraction

The GraphRAG pipeline should not depend directly on Ollama.

Instead it depends on a generation contract:

```text
TextGenerator
    ↓
generate(prompt)
    ↓
str
```

Possible implementations include:

* Ollama
* llama.cpp
* OpenAI-compatible APIs
* Hosted models
* Test doubles

## Prompt Grounding

The GraphRAG prompt explicitly tells the model to answer using retrieved graph knowledge.

The model should not invent relationships that are absent from the graph.

If the graph does not provide enough information, the desired behavior is to state that the available graph knowledge is insufficient.

## Graph Context

Graph context preserves structure.

Instead of:

```text
Ravi Sharma
ACC001
TXN001
```

the prompt receives:

```text
Ravi Sharma [customer]
--[owns]-->
ACC001 [account]

ACC001 [account]
--[initiated]-->
TXN001 [transaction]
```

This gives the language model both entities and relationship meaning.

## No-Seed Behavior

If no graph entity can be resolved from the query, graph retrieval cannot begin.

The GraphRAG pipeline therefore returns a deterministic fallback rather than asking the model to answer without grounding.

## Why Not Always Call the LLM?

Calling the LLM without retrieved graph evidence would convert the system from retrieval-augmented generation into ordinary generation.

The retrieval boundary is therefore enforced before generation.

## Pipeline Response

The response contains more than an answer.

It includes:

* Answer
* Resolved seed entities
* Retrieved entity count
* Retrieved relationship count
* Graph context

This metadata is important for observability and evaluation.

## Current Limitations

The initial GraphRAG pipeline does not yet implement:

* Hybrid vector + graph retrieval
* Semantic entity resolution
* Graph path ranking
* Relationship scoring
* Query decomposition
* Citation generation
* Token-budget-aware context compression
* Graph communities
* Retrieval evaluation

These are future improvements rather than requirements for the Day 5 architecture.

## Definition of Done

* [ ] Generation contract implemented.
* [ ] GraphRAG prompt builder implemented.
* [ ] Local Ollama generator implemented.
* [ ] GraphRAG response contract implemented.
* [ ] GraphRAG pipeline implemented.
* [ ] Empty retrieval handled without LLM call.
* [ ] Graph context passed to prompt builder.
* [ ] Prompt passed to generator.
* [ ] Retrieval metadata returned.
* [ ] Pipeline unit tests passing.
* [ ] Ollama adapter tests passing.
* [ ] GraphRAG script executing.
* [ ] Real local LLM generation verified.
* [ ] Complete GraphRAG regression passing.
* [ ] Full repository regression passing.
* [ ] Report completed.
* [ ] Scoreboard updated.
* [ ] Git changes committed and merged.
