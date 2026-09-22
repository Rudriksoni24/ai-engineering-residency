# Sprint 10 — Day 3: Persistent Storage and Databases

**Artifact:** Stateful Local Platform

## Objective

Deploy PostgreSQL and MinIO as lightweight stateful workloads in the
existing `ai-residency` kind cluster, then verify that their data
survives Pod deletion and recreation.

Reuse the existing `ai-platform` namespace and preserve the existing
Sprint 2 FastAPI deployment from Day 2.

This is a local learning platform, not a production database system.

## Prerequisites

- Sprint 10 Day 1 kind cluster exists.
- Sprint 10 Day 2 application deployment remains intact.
- Colima and Docker are available.
- The Kubernetes node is Ready.
- The available StorageClasses have been inspected.
- Existing Docker and Kubernetes data have been inventoried.
- Earlier PostgreSQL or MinIO volumes have not been deleted.

## Storage Concepts

### Ephemeral container storage

A container's writable filesystem is not suitable for durable
application data. Recreating the container or Pod can lose changes
stored only in that writable layer.

### PersistentVolume

A PersistentVolume, or PV, represents storage available to the
Kubernetes cluster.

A PV has capacity, access modes, a reclaim policy, and a storage
implementation.

### PersistentVolumeClaim

A PersistentVolumeClaim, or PVC, requests storage for a workload.

A claim specifies requirements such as capacity and access mode.

A matching PV may be provisioned dynamically by a StorageClass.

### StorageClass

A StorageClass defines how storage is provisioned.

Its availability depends on the Kubernetes environment.

Inspect the cluster before relying on dynamic provisioning.

### Access modes

`ReadWriteOnce` allows a volume to be mounted read-write by a
single node. It does not, by itself, prevent multiple Pods on that
same node from accessing the volume.

Day 3 uses one replica per stateful service and one claim per Pod.

### Reclaim policy

The reclaim policy determines what happens to the underlying PV
when its claim is deleted.

A `Delete` policy can cause provisioned storage and its data to
be deleted when the claim is removed.

Do not delete today's PVCs during ordinary cleanup.

### StatefulSet

A StatefulSet gives Pods stable ordinal identities and supports
stable storage claims generated from volumeClaimTemplates.

Examples:

`postgres-0`

`minio-0`

Deleting a StatefulSet-managed Pod causes a replacement with the
same ordinal identity.

The Pod can remount the same persistent claim.

### Headless Service

A headless Service (`clusterIP: None`) provides DNS identities
for StatefulSet Pods.

It is distinct from the normal client-facing ClusterIP Service.

## Architecture

```text
kind cluster: ai-residency
  |
  +-- Namespace: ai-platform
        |
        +-- Existing local-llm-api Deployment
        |
        +-- PostgreSQL
        |     |
        |     +-- Client Service: postgres:5432
        |     +-- Headless Service: postgres-headless
        |     +-- StatefulSet: postgres
        |           |
        |           +-- Pod: postgres-0
        |           +-- PVC: postgres-data-postgres-0
        |                 |
        |                 +-- PersistentVolume
        |
        +-- MinIO
              |
              +-- Client Service: minio:9000
              +-- Headless Service: minio-headless
              +-- StatefulSet: minio
                    |
                    +-- Pod: minio-0
                    +-- PVC: minio-data-minio-0
                          |
                          +-- PersistentVolume
```

## Workload Design

Use one PostgreSQL replica and one MinIO replica.

A second PostgreSQL or MinIO Pod is not a database replica simply
because a StatefulSet has been scaled to two.

Database replication requires explicit application-level
configuration and is outside Day 3 scope.

## Configuration

Place non-secret PostgreSQL configuration in a ConfigMap.

Place credentials in Kubernetes Secrets created locally.

Do not commit real credentials, passwords, access keys, or
base64-encoded credentials.

Base64 encoding is not encryption.

## PostgreSQL Persistence

PostgreSQL stores its data in a PVC mounted at its data directory.

Create a test table and insert a known marker.

Delete the PostgreSQL Pod, allow the StatefulSet to recreate it,
then query the marker.

The marker must remain present.

## MinIO Persistence

MinIO stores objects in a PVC mounted at `/data`.

Create a test bucket and upload an object.

Delete the MinIO Pod, allow the StatefulSet to recreate it,
then retrieve the same object.

The object's contents must match the original.

## Services

Use a headless Service for stable StatefulSet identities.

Use a separate ClusterIP Service for client connections.

PostgreSQL uses port 5432.

MinIO uses port 9000 for its API and port 9001 for its console.

## Resource Management

Use conservative CPU and memory requests and limits.

Check node capacity and existing workloads before deployment.

Do not duplicate existing datasets or start unnecessary local
services.

## Testing

Validate:

1. Namespace and StorageClass availability.
2. Kubernetes manifest acceptance.
3. Secret presence without printing credential values.
4. PVC binding.
5. StatefulSet readiness.
6. ClusterIP Service and endpoint availability.
7. PostgreSQL write/read operations.
8. PostgreSQL data preservation after Pod deletion.
9. MinIO object upload/download.
10. MinIO data preservation after Pod deletion.
11. Existing Day 2 application availability.
12. Existing application and repository regression tests.

Infrastructure integration checks are executed explicitly through
kubectl and container clients.

Ordinary pytest must not require a running Kubernetes cluster.

## Limitations

This setup is not highly available.

Both stateful services run on a single kind node.

Local kind storage is not an independent disaster-recovery copy.
Deleting the kind cluster or underlying Colima storage may destroy
data even when it survived Pod deletion.

Pod persistence is not equivalent to backup or disaster recovery.

Do not migrate existing PostgreSQL databases or MinIO buckets into
the new workloads without a separate migration and verification
plan.

## Day 3 Exit Gate

- [ ] Existing data inventory completed.
- [ ] Existing Day 2 application preserved.
- [ ] StorageClass verified.
- [ ] PostgreSQL PVC Bound.
- [ ] PostgreSQL StatefulSet Ready.
- [ ] PostgreSQL marker survives Pod deletion.
- [ ] MinIO PVC Bound.
- [ ] MinIO StatefulSet Ready.
- [ ] MinIO object survives Pod deletion.
- [ ] Credentials not committed.
- [ ] Resource usage remains acceptable.
- [ ] Existing local_llm tests pass.
- [ ] Repository regression passes.
- [ ] Engineering report contains actual evidence.
- [ ] Scoreboard updated only after validation.
- [ ] Day 3 branch committed and merged.

**Artifact:** Stateful Local Platform