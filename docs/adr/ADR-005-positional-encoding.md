# ADR-005: Positional Encoding Strategy

## Status

Accepted

## Context

Transformer self-attention does not inherently contain sequence-order information. The system therefore requires a mechanism to represent token positions.

## Decision

Use sinusoidal positional encoding based on the formulation introduced in the original Transformer architecture for this learning implementation.

The encoding will:

* Be deterministic.
* Require no learned positional parameters.
* Support configurable sequence lengths and embedding dimensions.
* Be added to token embeddings before attention layers.

## Consequences

### Positive

* Makes token order available to the model.
* Does not require training positional parameters.
* Provides a direct implementation of the original Transformer formulation.

### Negative

* This approach is not the only positional representation used by modern language models.
* Future experiments will compare learned positional embeddings and relative or rotary positional approaches.
