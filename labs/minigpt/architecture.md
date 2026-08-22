# MiniGPT Architecture

## Model Type

Decoder-only Transformer.

## Input

Token IDs:

(batch, sequence_length)

## Embedding Layer

Token embeddings:

(batch, sequence_length, d_model)

Positional embeddings:

(batch, sequence_length, d_model)

Combined:

(batch, sequence_length, d_model)

## Transformer Stack

N causal Transformer blocks.

Input and output:

(batch, sequence_length, d_model)

## Output

Final LayerNorm.

Language model head:

d_model → vocab_size

Final logits:

(batch, sequence_length, vocab_size)

## Causal Constraint

Token i cannot attend to token j when:

j > i

This allows the model to be trained for next-token prediction
without accessing future tokens.