# Sprint 10 — Day 1: Kubernetes Fundamentals

## Artifact

Local Kubernetes Cluster

---

## Objective

Understand the fundamental architecture of Kubernetes and create a
working local Kubernetes cluster suitable for the AI Engineering
Residency development environment.

The local environment is:

- macOS Apple Silicon M2
- 16 GB RAM
- Colima
- Docker
- kind
- kubectl

This is intentionally a local learning environment rather than a
production Kubernetes architecture.

---

# Docker vs Kubernetes

Docker runs containers.

Kubernetes orchestrates containers.

Docker is primarily responsible for building and running individual
containers.

Kubernetes manages groups of containerized workloads and continuously
attempts to keep the actual running system aligned with the declared
desired state.

```text
Docker
=
runs containers

Kubernetes
=
orchestrates containers