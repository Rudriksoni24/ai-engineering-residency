# Sprint 10 — Day 3: Stateful Local Platform

This directory contains the Day 3 PostgreSQL and MinIO Kubernetes
configurations.

## Existing-data preservation

Do not delete pre-existing Docker volumes, database containers,
MinIO containers, Kubernetes PVCs, or PVs.

The Day 3 StatefulSets create their own persistent claims.

## Namespace

Both services use the existing `ai-platform` namespace.

## PostgreSQL

- StatefulSet: `postgres`
- Pod: `postgres-0`
- Client Service: `postgres:5432`
- Headless Service: `postgres-headless`
- PVC: `postgres-data-postgres-0`

## MinIO

- StatefulSet: `minio`
- Pod: `minio-0`
- Client Service: `minio:9000`
- Console Service port: `9001`
- Headless Service: `minio-headless`
- PVC: `minio-data-minio-0`

## Secrets

Real credentials are created using `kubectl create secret`.

`secret.example.yaml` files are documentation only.

Never apply example Secret files with placeholder values.

Never commit passwords, access keys, or decoded Secret values.

## Deployment order

1. Inspect existing storage.
2. Confirm a working default StorageClass.
3. Apply the existing namespace.
4. Create actual Secrets locally.
5. Apply ConfigMaps.
6. Apply Services.
7. Apply StatefulSets.
8. Confirm PVCs are Bound.
9. Verify StatefulSet and Pod readiness.
10. Write/read persistent data.
11. Delete each Pod and verify data remains.

## Cleanup

Scaling StatefulSets to zero can free memory while preserving PVCs.

Do not delete PVCs, PVs, the kind cluster, or Colima storage during
ordinary cleanup.

Persistence across Pod replacement is not a backup strategy.