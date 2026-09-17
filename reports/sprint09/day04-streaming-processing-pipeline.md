# Sprint 9 — Day 4 Report

## Title

Spark Structured Streaming

## Artifact

Streaming Processing Pipeline

## Architecture

```text
Synthetic Transaction Producer
        |
        v
Kafka transactions topic
        |
        v
Spark Structured Streaming
        |
        v
JSON Parsing
        |
        v
Validation / Transformation
        |
        v
Streaming Sink