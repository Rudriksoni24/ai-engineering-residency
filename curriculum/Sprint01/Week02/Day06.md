# Week 2 Day 6

# Train Tiny Language Model

## Goal

Train the MiniGPT architecture using next-token prediction.

Build an end-to-end pipeline covering:

- Tokenization
- Dataset preparation
- Input and target creation
- Cross entropy loss
- Backpropagation
- Optimization
- Checkpointing
- Autoregressive generation

## Duration

- Data and tokenization: 25 minutes
- Dataset pipeline: 20 minutes
- Training loop: 45 minutes
- Generation and evaluation: 30 minutes

---

# Learning Objectives

By the end of this day, I should be able to:

- Convert text into token IDs.
- Create a vocabulary.
- Create input-target training pairs.
- Explain next-token prediction.
- Calculate cross entropy loss.
- Perform forward propagation.
- Perform backward propagation.
- Update model parameters.
- Track training loss.
- Save a model checkpoint.
- Generate text autoregressively.

---

# Training Objective

Given:

Input:

A B C

Target:

B C D

The model learns:

P(B | A)

P(C | A, B)

P(D | A, B, C)

---

# Tasks

- [ ] Implement tokenizer.
- [ ] Build vocabulary.
- [ ] Encode training text.
- [ ] Create input-target pairs.
- [ ] Create dataset.
- [ ] Create DataLoader.
- [ ] Implement cross entropy loss.
- [ ] Implement optimizer.
- [ ] Implement training loop.
- [ ] Track loss.
- [ ] Save checkpoint.
- [ ] Load checkpoint.
- [ ] Implement autoregressive generation.
- [ ] Compare generated output before and after training.

---

# Definition of Done

- [ ] Text converts to token IDs.
- [ ] Input-target pairs are correct.
- [ ] Loss decreases on a tiny dataset.
- [ ] Gradients are produced.
- [ ] Parameters change after optimization.
- [ ] Checkpoint can be saved.
- [ ] Checkpoint can be loaded.
- [ ] Model generates tokens autoregressively.
- [ ] Tests pass.
- [ ] Documentation completed.