# Sprint 10 — Day 2: Pods, Deployments, Services, Namespaces

**Artifact:** Kubernetes Application

## 1. Objective

Deploy the existing Sprint 2 Local LLM FastAPI service into the
Kubernetes cluster created during Sprint 10 Day 1.

The purpose is to understand how Kubernetes deploys, manages,
exposes, updates, and recovers an existing application.

The existing application must be reused.

Do not create a separate demonstration API.

## 2. Prerequisites

The existing development environment consists of:

- macOS Apple Silicon M2
- 16 GB RAM
- Python 3.12
- Colima
- Docker
- kind
- kubectl
- Root-level uv project

Existing Kubernetes cluster:

`ai-residency`

Existing Kubernetes context:

`kind-ai-residency`

## 3. Existing Application

The deployment target is the Sprint 2 Local LLM FastAPI service.

Application package:

`local_llm/`

Verified application entry point:

`local_llm.api.main:app`

Existing endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | API-process health |
| `/ready` | GET | Ollama runtime availability |
| `/v1/generate` | POST | LLM generation |

Existing runtime:

`local_llm.runtime.ollama_runtime.OllamaRuntime`

Existing service:

`local_llm.api.services.llm_service.LLMService`

The default generation model is `qwen2.5:3b`.

The API and Ollama runtime remain separate components.

## 4. Architecture

```text
MacBook
   |
   v
kubectl port-forward
   |
   v
Kubernetes Cluster
   |
   v
Namespace: ai-platform
   |
   v
Service: local-llm-api
   |
   v
Deployment: local-llm-api
   |
   v
ReplicaSet
   |
   v
FastAPI Pod
   |
   +---- /health
   |
   +---- /ready
   |
   +---- /v1/generate
                 |
                 v
             LLMService
                 |
                 v
            OllamaRuntime
                 |
                 v
          External Ollama
```

## 5. Pod

A Pod is the smallest deployable scheduling unit in Kubernetes.

A Pod contains one or more containers.

Containers inside the same Pod share a network namespace.

Today's application Pod contains one FastAPI container.

The Pod does not contain an independent copy of the Ollama model.

Pods are disposable.

A replacement Pod does not preserve the original Pod's identity
or in-memory application state.

## 6. ReplicaSet

A ReplicaSet maintains a desired number of matching Pods.

Example:

```text
Desired replicas = 2

Actual replicas = 1

ReplicaSet creates another Pod.
```

ReplicaSets are normally managed through Deployments.

## 7. Deployment

A Deployment declaratively manages application workloads.

```text
Deployment
    |
    v
ReplicaSet
    |
    v
Pods
```

Deployments support:

- Desired replica counts
- Rolling updates
- Rollout history
- Rollbacks
- Pod replacement
- Declarative workload configuration

The initial desired replica count is one.

## 8. Service

A Service provides stable networking for a group of Pods.

Pod IP addresses can change when Pods are replaced.

A Service provides a stable address that clients can use.

```text
Client
   |
   v
Service
   |
   +------+
   |      |
   v      v
 Pod A  Pod B
```

Today's Service is named:

`local-llm-api`

Its type is:

`ClusterIP`

## 9. Namespace

A Namespace organizes namespaced Kubernetes resources.

Today's namespace is:

`ai-platform`

Namespaces provide logical organization and resource scoping.

A Namespace alone does not guarantee network isolation.

## 10. Labels and Selectors

Labels are key-value metadata attached to Kubernetes resources.

Example:

```yaml
labels:
  app: local-llm-api
```

Selectors identify resources using matching labels.

Example:

```yaml
selector:
  app: local-llm-api
```

The Service selector must match the application Pod labels.

## 11. Desired Replicas

The Deployment initially declares:

```yaml
replicas: 1
```

The application will be temporarily scaled to two replicas.

It will then be scaled back to one replica to conserve memory.

## 12. Rolling Updates

A rolling update gradually replaces Pods associated with an
older Pod template with Pods associated with a newer template.

The Deployment manages the transition between ReplicaSets.

A controlled Pod-template change will demonstrate this behavior.

## 13. Self-Healing

If a Deployment-managed Pod is deleted, its ReplicaSet creates
a replacement to restore the desired replica count.

This restores the declared infrastructure state.

It does not automatically restore lost application data.

## 14. ClusterIP

ClusterIP exposes a Service inside the Kubernetes cluster.

Today's application uses ClusterIP.

Local testing uses kubectl port-forward.

## 15. NodePort

NodePort exposes a Service through a port on Kubernetes nodes.

NodePort is not required for today's application.

## 16. LoadBalancer

LoadBalancer requests an external load-balancing implementation.

A local kind cluster does not automatically provide a cloud
load balancer.

## 17. port vs targetPort

The Service port is the port exposed by the Service.

The targetPort is the destination port on the selected Pods.

Today's application uses:

```text
Service port: 80

Container port: 8000
```

## 18. Readiness Probe

A readiness probe determines whether a Pod is eligible to receive
normal application traffic.

A failing readiness probe removes the Pod from the set of ready
Service endpoints.

It does not automatically restart the container.

## 19. Liveness Probe

A liveness probe determines whether a container should be restarted.

Repeated liveness failures can cause a container restart.

The liveness probe should detect API-process failures rather than
temporary outages of external dependencies.

## 20. Ollama Dependency

The FastAPI application and Ollama are separate components.

The FastAPI application runs inside Kubernetes.

Ollama runs externally on the Mac.

Inside the Kubernetes Pod, localhost refers to the Pod's own
network namespace.

It does not refer to the Mac.

The Ollama endpoint must be configured explicitly.

Generation must not be reported as functional unless a real
generation request succeeds.

## 21. Resource Management

The initial API Deployment uses:

| Resource | Request | Limit |
|---|---:|---:|
| CPU | 100m | 1 CPU |
| Memory | 128Mi | 512Mi |

The allocation is intentionally small because the local
development machine has 16 GB RAM.

The model runtime is not duplicated inside the API Pods.

## 22. Kubernetes Debugging

Use the following sequence:

```text
kubectl get
    |
    v
kubectl describe
    |
    v
kubectl logs
    |
    v
kubectl get events
    |
    v
Inspect Service and EndpointSlices
    |
    v
Inspect configuration
```

Do not randomly modify YAML when a deployment fails.

## 23. Testing

Testing must be separated into:

1. Existing application unit tests.
2. Docker image validation.
3. Kubernetes manifest validation.
4. Live Kubernetes deployment verification.

Ordinary repository pytest must not depend on a running
Kubernetes cluster.

Existing local_llm tests must be reused.

## 24. Required Demonstrations

Day 2 must demonstrate:

1. Build the existing FastAPI application's container image.
2. Load the image into kind.
3. Create the ai-platform namespace.
4. Deploy the application.
5. Confirm the Pod reaches Running and Ready.
6. Confirm the Service has a working endpoint.
7. Port-forward the Service to the Mac.
8. Call the existing health endpoint.
9. Call the generation endpoint if Ollama is available.
10. Inspect Pod logs.
11. Scale from one replica to two.
12. Confirm both replicas become Ready.
13. Scale back to one replica.
14. Delete the Pod and demonstrate self-healing.
15. Demonstrate a controlled Deployment rollout.
16. Explain how the Service routes traffic to matching Pods.

## 25. Day 2 Scope Boundary

Do not introduce:

- PostgreSQL
- MinIO
- PersistentVolumeClaims
- Spark
- Airflow
- Jenkins
- SonarQube
- ArgoCD

Those technologies belong to later Sprint 10 days.

## 26. Day 2 Exit Criteria

Day 2 is complete when:

- The existing Sprint 2 FastAPI service runs inside Kubernetes.
- The ai-platform namespace exists.
- The Deployment and Service work.
- The existing health endpoint is reachable through the Service.
- Readiness and liveness are configured appropriately.
- Scaling works.
- Self-healing works.
- Rollout behavior has been demonstrated.
- Existing application tests still pass.
- Repository regression tests pass.

Generation through Ollama should also be demonstrated if the
external runtime is available and reachable.

Any unverified functionality must be documented.

Sprint exit criteria unlocked:

- Deploy applications into namespaces.
- Explain pods, nodes, deployments, and services.