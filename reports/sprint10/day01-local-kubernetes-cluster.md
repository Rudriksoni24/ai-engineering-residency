# Sprint 10 — Day 1: Kubernetes Fundamentals

**Artifact:** Local Kubernetes Cluster  
**Report path in repository:** `reports/sprint10/day01-local-kubernetes-cluster.md`  
**Branch:** `feature/sprint10-day01`  
**Cluster name:** `ai-residency`  
**Kubernetes distribution:** kind (Kubernetes in Docker)  
**Report status:** Implementation guide and validation record prepared; **cluster execution has not been independently verified in this chat.** Complete the evidence fields below using actual command output before marking Day 1 complete.

---

## 1. Objective and scope

Establish a lightweight, reproducible Kubernetes cluster on the existing macOS Apple Silicon M2 / 16 GB environment using Colima and Docker. Understand the control plane, nodes, Pods, container execution, API access, desired state, and declarative configuration. Inspect cluster and system workloads and optionally run **one temporary smoke-test Pod**, then remove it.

**In scope:** kind cluster configuration and creation; `kubectl` setup; cluster, node, namespace, system Pod, and runtime inspection; temporary scheduling smoke test; infrastructure validation and regression check.

**Out of scope:** the residency application, Deployments, Services, application namespaces, probes, storage, PostgreSQL, MinIO, Airflow, Spark, CI, and ArgoCD. These belong to later Sprint 10 days.

## 2. Environment and decisions

| Item | Day 1 choice or check |
| --- | --- |
| Host | macOS, Apple Silicon M2, 16 GB RAM (user-provided environment) |
| Python/project | Existing root-level `uv` project; no nested project or virtual environment |
| Container infrastructure | Existing Colima + Docker |
| Kubernetes distribution | **kind**, retained throughout Sprint 10 unless a concrete technical problem requires a change |
| Cluster topology | One kind control-plane node, also available for local learning workloads |
| Cluster name / context | `ai-residency` / `kind-ai-residency` |
| Repository config | `infra/kubernetes/cluster/kind-config.yaml` |
| Persistence | None added on Day 1 |
| Production equivalence | None claimed; this is an intentionally small local learning cluster |

**Decision rationale:** A single-node kind cluster reuses Docker/Colima, permits quick recreation, and avoids the extra CPU/RAM cost of a multi-node environment on a 16 GB laptop. It demonstrates control-plane and node fundamentals but does not demonstrate high availability, failure of independent worker machines, or production networking and storage.

## 3. Kubernetes architecture and concepts

```text
macOS M2
  └─ Colima Linux VM
      └─ Docker
          └─ kind node container: ai-residency-control-plane
              ├─ kube-apiserver ─── etcd
              ├─ kube-scheduler
              ├─ kube-controller-manager
              ├─ kubelet
              ├─ containerd (node-side runtime)
              └─ Kubernetes system Pods and temporary smoke-test Pod
```

**Docker versus Kubernetes:** Docker can build and run containers; Kubernetes describes and reconciles containerized workloads across nodes. In this setup, Docker runs the kind *node container*, while Kubernetes inside the node uses a container runtime to run its Pods. They operate at different layers; Kubernetes is not simply another container image builder.

**Resource hierarchy:** `Cluster → Node → Pod → Container`. A cluster has one or more nodes. A Pod is the smallest Kubernetes scheduling unit and may include one or more containers. A node is the machine or VM environment on which kubelet and the container runtime operate; kind represents a Kubernetes node as a Docker container.

| Component | Responsibility | What to inspect |
| --- | --- | --- |
| `kubectl` | CLI client for the Kubernetes API | `kubectl config current-context`, `kubectl cluster-info` |
| kube-apiserver | Accepts, authenticates/authorizes, and validates API requests; exposes cluster state through the API | `kubectl cluster-info`; API-server Pod in `kube-system` |
| etcd | Persistent key-value backing store for Kubernetes control-plane state, **not** a substitute for an application database | etcd Pod in `kube-system` |
| scheduler | Assigns unscheduled Pods to suitable nodes | `Node:` and scheduling events in `kubectl describe pod day01-smoke` |
| controller manager | Runs reconciliation controllers that act on differences between desired and observed state | controller-manager Pod; understand desired-vs-actual model |
| kubelet | Node agent that works to ensure assigned Pods' containers run as specified | `kubectl describe node ai-residency-control-plane` and Pod status |
| container runtime | Creates/starts/stops containers on a Kubernetes node; commonly containerd | `kubectl get nodes -o wide` or node description |
| Pod | Schedulable unit containing container(s) | temporary `day01-smoke` Pod |

**Desired state and reconciliation:** A user or controller submits a resource specification through the API. Controllers observe actual cluster state and act to reduce deviations from the declared state. The scheduler selects nodes for Pods that lack assignments; kubelet and the container runtime work to realize assigned Pods. A standalone Pod created with `kubectl run --restart=Never` **is not** the same as a Deployment: deleting it will not cause a Deployment-style replacement. Replica reconciliation and self-healing demonstrations belong to Day 2.

**Imperative versus declarative:** `kubectl run ...` imperatively requests a one-off object; a version-controlled YAML specification declares a desired object configuration. The kind cluster config below is declarative input to **kind's cluster-creation tool**, not itself a Kubernetes Deployment manifest.

## 4. Files created and repository boundaries

```text
curriculum/Sprint10/Day01.md
infra/kubernetes/cluster/kind-config.yaml
reports/sprint10/day01-local-kubernetes-cluster.md
scoreboard.md                       # update only after validation
```

Do not create application manifests, databases, storage claims, CI workflows, or GitOps configurations on Day 1. Do not commit local kubeconfig files, generated secrets, logs, volume contents, or large ML artifacts.

### 4.1 Cluster configuration — `infra/kubernetes/cluster/kind-config.yaml`

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
```

A single control-plane node is intentionally used. kind's defaults supply Kubernetes system components and networking; the configuration does not promise production networking or persistent application data.

## 5. Exact setup and creation commands

Run from the repository root. These commands are **instructions**, not a claim that they have been executed on your laptop.

```bash
cd ~/Desktop/ai-engineering-residency/ai-engineering-residency
git status --short
git checkout main
git pull
git checkout -b feature/sprint10-day01

mkdir -p curriculum/Sprint10 infra/kubernetes/cluster reports/sprint10
touch curriculum/Sprint10/Day01.md
touch reports/sprint10/day01-local-kubernetes-cluster.md

cat > infra/kubernetes/cluster/kind-config.yaml <<'YAML'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
YAML
```

**Prerequisite checks:**

```bash
colima status
# Only if Colima is stopped:
colima start

docker version
docker info
docker context show

kubectl version --client || brew install kubectl
kind version || brew install kind
```

`docker info` must succeed before cluster creation. Check current clusters before making changes:

```bash
kind get clusters
```

If `ai-residency` already exists, inspect it first: `kubectl cluster-info --context kind-ai-residency`. **Do not delete an existing cluster blindly:** deletion removes its Kubernetes objects and any data living only inside its node container. Reuse a healthy matching cluster or delete it only if you knowingly want a clean, disposable recreation.

Create the cluster if it does not yet exist:

```bash
kind create cluster \
  --name ai-residency \
  --config infra/kubernetes/cluster/kind-config.yaml
kubectl config current-context
```

Expected context: `kind-ai-residency`.

## 6. Infrastructure validation: commands, pass conditions, evidence

The following are separate from the ordinary Python unit-test suite. Copy actual evidence into the table after running the commands; do not replace failed output with example success output.

| Check | Command | Passing condition | Actual output / observation |
| --- | --- | --- | --- |
| Cluster registered | `kind get clusters` | `ai-residency` listed | **PENDING — fill from terminal** |
| Correct context | `kubectl config current-context` | `kind-ai-residency` | **PENDING** |
| API reachable | `kubectl cluster-info` | Control plane endpoint reachable without error | **PENDING** |
| Node healthy | `kubectl get nodes -o wide` | `ai-residency-control-plane` status `Ready` | **PENDING** |
| Node component/runtime inspection | `kubectl describe node ai-residency-control-plane` | Ready condition true; inspect runtime and resource details | **PENDING** |
| System namespaces | `kubectl get namespaces` | Typical namespaces include `default`, `kube-system`, `kube-public`, `kube-node-lease` | **PENDING** |
| System Pods | `kubectl get pods -A -o wide` | Core control-plane and system networking Pods healthy after initialization | **PENDING** |
| Control plane | `kubectl get pods -n kube-system` | API server, etcd, scheduler, controller manager and relevant networking Pods not stuck in failure states | **PENDING** |
| Docker-side kind node | `docker ps --filter name=ai-residency-control-plane` | Running kind node container visible | **PENDING** |

**Commands to run together:**

```bash
kind get clusters
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
kubectl describe node ai-residency-control-plane
kubectl get namespaces
kubectl get pods -A -o wide
kubectl get pods -n kube-system
docker ps --filter name=ai-residency-control-plane
```

System Pods can temporarily be `Pending` or `ContainerCreating` during initialization. Recheck after startup; persistent errors need diagnosis, not a premature success mark. `kubectl top` may be unavailable if metrics-server is not installed, and it is **not a Day 1 pass condition**.

## 7. Optional temporary Pod smoke test

This verifies scheduling and node execution; it does **not** build the Day 2 application.

```bash
kubectl run day01-smoke \
  --image=registry.k8s.io/pause:3.10 \
  --restart=Never

kubectl wait --for=condition=Ready pod/day01-smoke --timeout=120s
kubectl get pod day01-smoke -o wide
kubectl describe pod day01-smoke

kubectl delete pod day01-smoke
kubectl get pod day01-smoke
```

**Pass condition:** The Pod starts and reaches Ready/Running, its node assignment and events can be inspected, and it is deleted afterward. Record below:

- Pod image pull/start result: **PENDING**
- Assigned node: **PENDING**
- Any warning events: **PENDING**
- Deletion confirmed: **PENDING**

If the image cannot be pulled, inspect Pod events and Docker/Colima connectivity before changing anything. The `pause` image is deliberately a minimal smoke workload, not an AI application or an application health check.

## 8. Regression checks, evidence, and status

The existing project test suite should remain independent of an active Kubernetes cluster.

```bash
uv run pytest -v
# Only if Ruff is configured for this repository:
uv run ruff check .

git status --short
git diff --check
```

| Check | Result / notes |
| --- | --- |
| `uv run pytest -v` | **PENDING — record total passed/failed and any relevant failures** |
| `uv run ruff check .` (if configured) | **PENDING / NOT APPLICABLE** |
| `git diff --check` | **PENDING** |
| Untracked/generated files inspected | **PENDING** |

If tests fail, distinguish a Day 1 regression from a pre-existing issue; do not claim green tests without evidence. No normal Python test should require a live Kubernetes cluster.

## 9. Troubleshooting approach

Diagnose in sequence, starting with the observable state:

```text
kubectl get → kubectl describe → kubectl logs (where meaningful)
→ events → networking / endpoints (when relevant) → configuration
```

| Symptom | First checks | Likely next action |
| --- | --- | --- |
| Docker daemon unavailable | `colima status`, `docker context show`, `docker info` | Start Colima or correct Docker context before retrying kind |
| `kubectl` cannot connect | `kubectl config current-context`, `kind get clusters`, `kubectl cluster-info --context kind-ai-residency` | Select the intended context; verify node container and Colima |
| Node `NotReady` | `kubectl describe node ai-residency-control-plane`, `kubectl get pods -n kube-system`, `docker ps` | Read node conditions and system Pod events; check VM resources |
| System Pod `Pending` | `kubectl describe pod <actual-name> -n kube-system` | Inspect scheduler/events; do not guess at YAML |
| `ImagePullBackOff` smoke Pod | `kubectl describe pod day01-smoke` | Read exact image-pull error; check network/registry accessibility |
| Colima VM low on RAM/disk | `colima status`, `docker system df`, `kubectl describe node ai-residency-control-plane` | Stop unrelated heavy local services; avoid indiscriminate deletion of project data |

Do not delete or recreate the cluster as the first troubleshooting step. Preserve actual error output for diagnosis.

## 10. Engineering tradeoffs and limitations

1. **One node trades high availability for low resource usage.** The learning cluster cannot prove failover between independent worker machines or a redundant control plane.
2. **kind nodes are Docker containers.** This makes the cluster reproducible locally, but container-level node failure differs from physical-host failure.
3. **Control plane and workloads share the same node.** This is acceptable for local education, not a model for production control-plane isolation.
4. **The cluster is disposable.** Kubernetes object and local node state may be lost on deletion; durable application storage is explicitly a later topic.
5. **A Running Pod is not proof of business correctness.** Kubernetes can check process state and declared probes, but cannot establish that an ML prediction or banking calculation is correct.
6. **A one-off Pod is not a Deployment.** Deleting `day01-smoke` will not trigger automatic Pod recreation; reconciliation of replica counts is demonstrated on Day 2.
7. **Kubernetes Secrets are not addressed today.** Do not embed credentials in cluster manifests or publish kubeconfig artifacts in the repository.
8. **No production claims.** This exercise does not cover managed control planes, production-grade security, observability, disaster recovery, external load balancers, or multi-node resilience.

## 11. Day 1 outcomes and explicit exit gate

Tick each item **only after observing it locally**:

- [ ] `kind get clusters` lists `ai-residency`.
- [ ] `kubectl config current-context` is `kind-ai-residency`.
- [ ] `kubectl cluster-info` reaches the Kubernetes API.
- [ ] `kubectl get nodes` shows `ai-residency-control-plane` as `Ready`.
- [ ] Kubernetes system Pods are healthy after initialization.
- [ ] Node, system namespaces, system Pods, and runtime have been inspected.
- [ ] Temporary smoke Pod was scheduled and removed, if this optional validation was used.
- [ ] `uv run pytest -v` completed with no new regression attributable to Day 1.
- [ ] Curriculum, kind config, report, and `scoreboard.md` changes were reviewed.
- [ ] Day 1 status and Sprint exit checkbox were updated **only after validation**.

**Current verification status:** Not yet evidenced in this chat. The report is complete as a documentation artifact, but the hands-on Day 1 milestone remains **pending until the user executes and verifies the commands**.

### Learning questions to answer before advancing

1. If the node's container runtime is working but the control plane is unreachable, which operations can still happen locally, and which API-driven operations fail?
2. What exactly maintains a Deployment's desired replica count? Why does deleting a standalone `kubectl run --restart=Never` Pod not necessarily bring it back?
3. Could a Kubernetes Pod be `Running` while an ML service gives incorrect predictions? What different checks would reveal each failure?

## 12. Scoreboard update after verified completion

Add the Sprint 10 table according to the existing curriculum, preserving all seven exact titles/artifacts. **Do not mark any later day complete.** After the Day 1 gate actually passes, change only:

```markdown
| Day 1 | Kubernetes Fundamentals | ✅ | Local Kubernetes Cluster |
```

and the single criterion:

```markdown
- [x] Run a local Kubernetes cluster.
```

Before validation, retain Day 1 as `⚪` and the criterion unchecked.

## 13. Git workflow after the exit gate

```bash
# Review the exact changes and tests first.
git status --short
git diff --check
uv run pytest -v

git add \
  curriculum/Sprint10/Day01.md \
  infra/kubernetes/cluster/kind-config.yaml \
  reports/sprint10/day01-local-kubernetes-cluster.md \
  scoreboard.md

git diff --cached
git commit -m "feat(sprint10): add local Kubernetes cluster"
git push -u origin feature/sprint10-day01

# Merge only once Day 1 is complete.
git checkout main
git pull
git merge --no-ff feature/sprint10-day01 \
  -m "merge: complete sprint10 day01 Kubernetes fundamentals"
git push origin main
git branch -d feature/sprint10-day01
```

Keep the kind cluster for Day 2 if continuing immediately. To reclaim resources **only if you accept losing this cluster's disposable state**:

```bash
kind delete cluster --name ai-residency
```

Recreate from the tracked configuration when needed:

```bash
kind create cluster --name ai-residency \
  --config infra/kubernetes/cluster/kind-config.yaml
```

---

**End-of-day conclusion (fill after verification):**  
Cluster status: **VERIFIED**  
System Pods: **VERIFIED**  
Smoke test: **VERIFIED**  
Repository tests: **VERIFIED**  
Day 1 exit gate: **VERIFIED**
