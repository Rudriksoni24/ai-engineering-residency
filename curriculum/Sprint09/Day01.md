# Sprint 9 — Day 1: Kafka Fundamentals

## Artifact

Local Kafka Environment

## Objective

Understand Kafka's fundamental architecture and operate a local Kafka broker
using Docker and KRaft mode.

## Core Concepts

### Event / Record / Message

An event is a fact that occurred in a system.

Example:

```json
{
  "transaction_id": "txn-001",
  "account_id": "acc-001",
  "amount": 1250.50,
  "currency": "INR",
  "transaction_type": "purchase"
}