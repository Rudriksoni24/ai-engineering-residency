# AI Engineering Residency — Sprint Scoreboard

## Status Legend

- 🟢 Completed
- 🟡 In Progress
- 🔴 Blocked
- ⚪ Not Started

---

# Overall Residency Roadmap

| Sprint | Target | Status |
|---|---|---|
| Sprint 0 | Engineering Environment | 🟢 |
| Sprint 1 | Understand and Build a Mini Transformer | 🟢 |
| Sprint 2 | Run and Engineer Local LLM Systems | 🟢 |
| Sprint 3 | Build Production-Style RAG | 🟢 |
| Sprint 4 | Build GraphRAG | 🟢 |
| Sprint 5 | Build Agent Fundamentals | 🟢 |
| Sprint 6 | Build Stateful and Multi-Agent Workflows | 🟢 |
| Sprint 7 | Adapt Local Models with LoRA and Understand Alignment | 🟢 |
| Sprint 8 | Build Traditional ML and MLflow Systems | 🟡 |
| Sprint 9 | Build Streaming Data Pipelines | ⚪ |
| Sprint 10 | Deploy with Kubernetes and CI/CD | ⚪ |
| Sprint 11 | Build Banking Portfolio Systems | ⚪ |
| Sprint 12 | Harden, Evaluate, and Productionize | ⚪ |

---

# Sprint 1 — AI/ML Foundations and Mini Transformer

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Environment Foundation | 🟢 | Development Environment |
| Day 2 | Professional Python Environment | 🟢 | Python Project Template |
| Day 3 | PyTorch Fundamentals | 🟢 | Neural Network Lab |
| Day 4 | Vector Math and Similarity | 🟢 | Embedding Foundations |
| Day 5 | Tokenizer From Scratch | 🟢 | Tokenizer |
| Day 6 | Embeddings | 🟢 | Embedding Engine |
| Day 7 | Positional Encoding | 🟢 | Positional Encoding Lab |
| Day 8 | Self-Attention and Q/K/V | 🟢 | Attention Engine |
| Day 9 | Multi-Head Attention | 🟢 | Multi-Head Attention |
| Day 10 | Transformer Block | 🟢 | Transformer Block |
| Day 11 | Attention Is All You Need | 🟢 | Paper Implementation |
| Day 12 | MiniGPT Architecture | 🟢 | MiniGPT |
| Day 13 | Train Tiny Language Model | 🟢 | Trained MiniGPT |
| Day 14 | Sprint Review and Integration | 🟢 | Sprint 1 Integration |

## Sprint Exit Criteria

- [ ] Explain the complete token-to-transformer pipeline.
- [ ] Implement positional encoding without copying a tutorial.
- [ ] Implement scaled dot-product attention.
- [ ] Explain Query, Key, and Value.
- [ ] Implement multi-head attention.
- [ ] Build a Transformer block.
- [ ] Train a tiny language model.
- [ ] Explain the architecture of Attention Is All You Need.

---

# Sprint 2 — Local LLM Systems

**Target:** Run, inspect, serve, benchmark, and integrate local/on-premise LLMs.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Local LLM Architecture and Runtime Landscape | 🟢 | Local LLM Architecture Notes |
| Day 2 | Ollama Fundamentals and Local Models | 🟢 | Ollama Model Runner |
| Day 3 | Model Anatomy and Quantization | 🟢 | Model Comparison Report |
| Day 4 | Local Inference Engineering | 🟢 | Streaming and Structured Output Lab |
| Day 5 | llama.cpp and GGUF | 🟢 | Direct Local Inference Benchmark |
| Day 6 | Local LLM Inference Service | 🟢 | FastAPI Local LLM Service |
| Day 7 | Sprint Integration and Evaluation | 🟢 | Local LLM Platform |

## Sprint Exit Criteria

- [ ] Run at least two LLMs locally.
- [ ] Explain model parameters, context windows, and token generation.
- [ ] Explain FP32, FP16, INT8, and low-bit quantization.
- [ ] Understand GGUF and why it is useful for local inference.
- [ ] Compare Ollama and llama.cpp.
- [ ] Implement streaming inference.
- [ ] Implement structured output validation.
- [ ] Expose a local model through an API.
- [ ] Benchmark latency and throughput.
- [ ] Document hardware and memory constraints.

---

# Sprint 3 — Production-Style RAG

**Target:** Build an end-to-end local RAG system with ingestion, retrieval, reranking, evaluation, and citations.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Embeddings and Semantic Search | 🟢 | Semantic Search Engine |
| Day 2 | Document Ingestion Pipeline | 🟢 | Document Ingestion Service |
| Day 3 | Chunking Strategies and Metadata | 🟢 | Chunking Evaluation Lab |
| Day 4 | Vector Databases and Hybrid Search | 🟢 | Local Vector Store |
| Day 5 | End-to-End RAG Pipeline | 🟢 | Local RAG Application |
| Day 6 | Reranking and RAG Evaluation | 🟢 | Retrieval Evaluation Suite |
| Day 7 | Production Integration | 🟢 | Banking Knowledge Assistant |

## Sprint Exit Criteria

- [ ] Build an ingestion pipeline.
- [ ] Compare chunking strategies.
- [ ] Generate and store embeddings locally.
- [ ] Implement semantic search.
- [ ] Implement metadata filtering.
- [ ] Implement hybrid retrieval.
- [ ] Add reranking.
- [ ] Generate grounded answers with sources.
- [ ] Evaluate retrieval quality.
- [ ] Evaluate answer quality.

---

# Sprint 4 — GraphRAG

**Target:** Build a graph-based retrieval system for connected enterprise knowledge.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Knowledge Graph Fundamentals | 🟢 | Graph Modeling Lab |
| Day 2 | Entity and Relationship Extraction | 🟢 | Knowledge Extraction Pipeline |
| Day 3 | Graph Storage and Querying | 🟢 | Local Knowledge Graph |
| Day 4 | Graph Retrieval | 🟢 | Graph Retrieval Engine |
| Day 5 | GraphRAG Architecture | 🟢 | GraphRAG Pipeline |
| Day 6 | Compare Vector RAG vs GraphRAG | 🟢 | Retrieval Comparison Report |
| Day 7 | Sprint Integration | 🟢 | Banking Graph Intelligence System |

## Sprint Exit Criteria

- [ ] Model entities and relationships.
- [ ] Extract entities from documents.
- [ ] Build and query a knowledge graph.
- [ ] Implement graph traversal.
- [ ] Combine graph retrieval with LLM generation.
- [ ] Compare GraphRAG with vector RAG.
- [ ] Explain when GraphRAG is unnecessary.

---

# Sprint 5 — Agent Fundamentals

**Target:** Build reliable tool-using AI agents.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Agent Architecture and ReAct | 🟢 | Agent Architecture Lab |
| Day 2 | Tool Calling | 🟢 | Tool Registry |
| Day 3 | Planning and Execution | 🟢 | Planning Agent |
| Day 4 | Memory Fundamentals | 🟢 | Agent Memory Layer |
| Day 5 | Structured Outputs and Guardrails | 🟢 | Reliable Agent Contracts |
| Day 6 | Agent Evaluation | 🟢 | Agent Test Harness |
| Day 7 | Sprint Integration | 🟢 | Research and Analysis Agent |

## Sprint Exit Criteria

- [ ] Explain the ReAct pattern.
- [ ] Implement tool calling.
- [ ] Build a tool registry.
- [ ] Implement an agent execution loop.
- [ ] Validate structured outputs.
- [ ] Handle tool failures.
- [ ] Separate short-term and long-term memory concepts.
- [ ] Build tests for agent behavior.

---

# Sprint 6 — Stateful and Multi-Agent Workflows

**Target:** Build durable, observable, stateful multi-agent systems.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Stateful Agent Workflows | 🟢 | Workflow State Machine |
| Day 2 | Workflow Graphs | 🟢 | Graph-Based Agent Workflow |
| Day 3 | Persistence and Checkpointing | 🟢 | Persistent Agent State |
| Day 4 | Multi-Agent Coordination | 🟢 | Coordinator and Worker Agents |
| Day 5 | Human-in-the-Loop | 🟢 | Approval Workflow |
| Day 6 | Failure Recovery and Retry | 🟢 | Resilient Workflow Engine |
| Day 7 | Sprint Integration | 🟢 | Multi-Agent Operations System |

## Sprint Exit Criteria

- [ ] Persist workflow state.
- [ ] Resume interrupted workflows.
- [ ] Implement conditional routing.
- [ ] Coordinate multiple agents.
- [ ] Implement retries and failure handling.
- [ ] Add human approval checkpoints.
- [ ] Trace workflow execution.

---

# Sprint 7 — LoRA and Alignment

**Target:** Adapt local models and understand modern alignment techniques.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Fine-Tuning Fundamentals | 🟢 | Fine-Tuning Study Lab |
| Day 2 | LoRA Mathematics and Architecture | 🟢 | LoRA Implementation |
| Day 3 | PEFT and Local Fine-Tuning | 🟢 | Adapted Local Model |
| Day 4 | Dataset Preparation for Fine-Tuning | 🟢 | Training Dataset Pipeline |
| Day 5 | RLHF Concepts | 🟢 | Alignment Architecture Notes |
| Day 6 | Direct Preference Optimization | 🟢 | Preference Optimization Lab |
| Day 7 | Sprint Integration | 🟢 | Domain-Adapted Local Model |

## Sprint Exit Criteria

- [ ] Explain why full fine-tuning is expensive.
- [ ] Explain low-rank adaptation.
- [ ] Train or adapt a local model using LoRA/PEFT.
- [ ] Prepare instruction data.
- [ ] Explain RLHF at a systems level.
- [ ] Explain reward models.
- [ ] Explain DPO.
- [ ] Compare LoRA adaptation with RAG.

---

# Sprint 8 — Traditional ML and MLflow

**Target:** Build reproducible ML training and experiment tracking systems.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Classical ML Pipeline | 🟢 | ML Pipeline |
| Day 2 | Feature Engineering | ⚪ | Feature Engineering Lab |
| Day 3 | Fraud Detection Modeling | ⚪ | Fraud Detection Model |
| Day 4 | Experiment Tracking with MLflow | ⚪ | MLflow Tracking System |
| Day 5 | Model Registry | ⚪ | Model Lifecycle Pipeline |
| Day 6 | Data and Model Validation | ⚪ | Validation Suite |
| Day 7 | Sprint Integration | ⚪ | Reproducible ML Platform |

## Sprint Exit Criteria

- [ ] Build a complete ML pipeline.
- [ ] Track experiments with MLflow.
- [ ] Compare multiple experiments.
- [ ] Register a model.
- [ ] Version model artifacts.
- [ ] Track parameters and metrics.
- [ ] Build reproducible training runs.

---

# Sprint 9 — Streaming Data Pipelines

**Target:** Build batch and streaming data systems for ML and AI workloads.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Kafka Fundamentals | ⚪ | Local Kafka Environment |
| Day 2 | Kafka Producers and Consumers | ⚪ | Event Pipeline |
| Day 3 | PySpark Fundamentals | ⚪ | PySpark Data Processing |
| Day 4 | Spark Structured Streaming | ⚪ | Streaming Processing Pipeline |
| Day 5 | Airflow Orchestration | ⚪ | Data Workflow DAG |
| Day 6 | Delta Lake and Data Contracts | ⚪ | Lakehouse Pipeline |
| Day 7 | Feast Feature Store | ⚪ | Feature Serving Pipeline |

## Sprint Exit Criteria

- [ ] Run Kafka locally.
- [ ] Build producers and consumers.
- [ ] Process data with PySpark.
- [ ] Build a streaming pipeline.
- [ ] Orchestrate workflows with Airflow.
- [ ] Understand Delta Lake fundamentals.
- [ ] Implement data contracts with Pydantic.
- [ ] Understand offline and online features.
- [ ] Use a feature store.

---

# Sprint 10 — Kubernetes and CI/CD

**Target:** Deploy the AI/ML platform into a local Kubernetes environment.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Kubernetes Fundamentals | ⚪ | Local Kubernetes Cluster |
| Day 2 | Pods, Deployments, Services, Namespaces | ⚪ | Kubernetes Application |
| Day 3 | Persistent Storage and Databases | ⚪ | Stateful Local Platform |
| Day 4 | Deploy Airflow and Spark | ⚪ | Kubernetes Data Platform |
| Day 5 | Docker and Artifact Management | ⚪ | Container and Artifact Pipeline |
| Day 6 | Jenkins, Pytest, and SonarQube | ⚪ | CI Quality Pipeline |
| Day 7 | ArgoCD and GitOps | ⚪ | GitOps Deployment Platform |

## Sprint Exit Criteria

- [ ] Run a local Kubernetes cluster.
- [ ] Deploy applications into namespaces.
- [ ] Explain pods, nodes, deployments, and services.
- [ ] Configure persistent storage.
- [ ] Connect workloads to PostgreSQL and S3-compatible storage.
- [ ] Containerize Python services.
- [ ] Build and test with CI.
- [ ] Run code quality checks.
- [ ] Understand artifact repositories.
- [ ] Deploy through ArgoCD/GitOps.

---

# Sprint 11 — Banking AI Portfolio Systems

**Target:** Build portfolio-grade systems focused on investment banking and financial operations.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | Banking System Architecture | ⚪ | Banking AI Architecture |
| Day 2 | Reconciliation Agent | ⚪ | Reconciliation Agent |
| Day 3 | Fraud Detection System | ⚪ | Fraud Detection Pipeline |
| Day 4 | Banking Knowledge RAG | ⚪ | Financial Knowledge Assistant |
| Day 5 | Investigation and Research Agent | ⚪ | Investigation Agent |
| Day 6 | Risk and Exception Workflow | ⚪ | Exception Management System |
| Day 7 | Portfolio Integration | ⚪ | Banking AI Platform |

## Sprint Exit Criteria

- [ ] Build a reconciliation workflow.
- [ ] Build a fraud detection pipeline.
- [ ] Build a banking RAG system.
- [ ] Build an investigation agent.
- [ ] Include audit trails.
- [ ] Include human approval where required.
- [ ] Demonstrate failure handling.
- [ ] Document architecture decisions.

---

# Sprint 12 — Hardening, Evaluation, and Productionization

**Target:** Turn prototypes into reliable engineering systems.

| Day | Topic | Status | Artifact |
|---|---|---|---|
| Day 1 | AI/ML Evaluation Framework | ⚪ | Evaluation Harness |
| Day 2 | RAG Evaluation | ⚪ | RAG Evaluation Report |
| Day 3 | Agent Evaluation | ⚪ | Agent Evaluation Suite |
| Day 4 | Observability and Tracing | ⚪ | Observability Stack |
| Day 5 | Security and Guardrails | ⚪ | Security Review |
| Day 6 | Performance and Load Testing | ⚪ | Performance Report |
| Day 7 | Final Portfolio Review | ⚪ | Production-Ready AI Portfolio |

## Sprint Exit Criteria

- [ ] Define measurable system quality metrics.
- [ ] Evaluate retrieval.
- [ ] Evaluate generation.
- [ ] Evaluate agent behavior.
- [ ] Implement tracing and observability.
- [ ] Document security boundaries.
- [ ] Perform failure testing.
- [ ] Perform performance testing.
- [ ] Complete architecture reviews.
- [ ] Produce portfolio documentation.

---

# Final Residency Deliverables

By the end of the residency, the repository should contain:

```text
ai-engineering-residency/
│
├── curriculum/
├── labs/
├── models/
├── training/
├── local-llm/
├── rag/
├── graphrag/
├── agents/
├── fine-tuning/
├── ml/
├── data-platform/
├── infrastructure/
├── banking-projects/
├── evaluation/
├── docs/
│   ├── adr/
│   ├── architecture/
│   └── runbooks/
├── tests/
└── scoreboard.md