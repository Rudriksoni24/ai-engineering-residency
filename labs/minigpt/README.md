# MiniGPT

A small decoder-only Transformer language model built from reusable
components implemented during the AI Engineering Residency.

## Architecture

Input Token IDs
        ↓
Token Embeddings
        +
Positional Embeddings
        ↓
N × Transformer Blocks
        ↓
Final LayerNorm
        ↓
Language Model Head
        ↓
Vocabulary Logits

## Input

(batch, sequence_length)

## Output

(batch, sequence_length, vocab_size)

## Current Status

Architecture implemented.

Training and text generation are implemented separately.

## Limitations

- Educational-scale model.
- No pretrained weights.
- No KV caching.
- No production inference optimization.

# Training Pipeline

Text
→ Tokenizer
→ Token IDs
→ Next-Token Dataset
→ MiniGPT
→ Vocabulary Logits
→ Cross Entropy Loss
→ Backpropagation
→ AdamW
→ Updated Parameters

## Training Objective

The model predicts the next token at every position.

Input:

A B C D

Target:

B C D E

## Sanity Check

Before training on larger data, the model must demonstrate the ability
to overfit a small dataset.