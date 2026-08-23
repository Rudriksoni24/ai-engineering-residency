# Week 02 Integration Pipeline Documentation

## 🔒 Engineering Quality & Reproducibility
To prevent the "Shattered Debugging Loop" where successive test executions display varying numerical behaviors due to floating-point randomness, this repository establishes a strict global seed architecture.

* **Deterministic Global Seed Entry**: `42`
* **Seeded Entities**: 
  - Python Built-in Core Engine (`random.seed(42)`)
  - NumPy Numeric Processing Space (`np.random.seed(42)`)
  - PyTorch Initialization Graph (`torch.manual_seed(42)`)
  - Backprop CUDA Execution Core (`torch.backends.cudnn.deterministic = True`)

Every execution of `run_pipeline.py` will generate the exact same starting loss metrics, weight gradients, and final token generations down to the last decimal position, allowing for reliable debugging and cross-environment verification.


# Week 02 Integration Pipeline & Tensor-Shape Audit

Shape confusion is one of the most common sources of silent machine learning bugs. When dimensions align by accident, models can train without crashing while computing completely broken operations (like accidentally calculating loss against an out-of-order sequence).

The table below outlines the exact mathematical dimensions tracking tensors through our master integration framework.

## 📊 Tensor-Shape Audit Table

These values represent a specific forward pass snapshot using the config parameters from `run_pipeline.py`:
* **Batch Size ($B$)** = `4`
* **Sequence Length ($T$)** = `16`
* **Model Dimensions ($d_{model}$)** = `128`
* **Vocabulary Size ($V$)** = `21`

| Stage | Abstract Formula Shape | Actual Implementation Value Example |
| :--- | :--- | :--- |
| **Raw text** | `String` | `"machine learning is fun..."` (84 characters total) |
| **Token IDs** | `(tokens,)` | `(84,)` (Flat 1D list of integer indices) |
| **Dataset input** | `(batch, sequence)` | `(4, 16)` |
| **Dataset target** | `(batch, sequence)` | `(4, 16)` (Shifted right by exactly 1 token position) |
| **Token embeddings** | `(batch, sequence, d_model)` | `(4, 16, 128)` |
| **Position embeddings** | `(sequence, d_model)` | `(16, 128)` (Broadcasts seamlessly across the `batch` dimension) |
| **Transformer output** | `(batch, sequence, d_model)` | `(4, 16, 128)` |
| **Vocabulary logits** | `(batch, sequence, vocab_size)` | `(4, 16, 21)` |
| **Flattened logits** | `(batch × sequence, vocab_size)` | `(64, 21)` (Reshaped via `.reshape(B * T, V)`) |
| **Flattened targets** | `(batch × sequence)` | `(64,)` (Reshaped via `.reshape(B * T)`) |
| **Loss** | `Scalar` | `()` (0-dimensional float tensor tracking Cross-Entropy) |

---

## 🔒 Engineering Quality & Reproducibility
To prevent the "Shattered Debugging Loop" where successive test executions display varying numerical behaviors due to floating-point randomness, this repository establishes a strict global seed architecture.

* **Deterministic Global Seed Entry**: `42`
* **Seeded Entities**: 
  - Python Built-in Core Engine (`random.seed(42)`)
  - NumPy Numeric Processing Space (`np.random.seed(42)`)
  - PyTorch Initialization Graph (`torch.manual_seed(42)`)
  - Backprop CUDA Execution Core (`torch.backends.cudnn.deterministic = True`)

Every execution of `run_pipeline.py` will generate the exact same starting loss metrics, weight gradients, and final token generations down to the last decimal position, allowing for reliable debugging and cross-environment verification.

# Week 02 Architectural Failure Experiments Log

## 🧪 Failure 1 — Future Token Leakage
* **Action**: Removed causal mask string parameter configurations inside the master module loop.
* **Access to Future Targets**: Confirmed. Bidirectional attention allows token positions to look directly at upcoming target elements.
* **Metric Distortion**: Loss collapses to near-zero artificially because the model copies the target answer from position $t+1$ instead of learning language dynamics.

## 🧪 Failure 2 — Wrong Target Alignment
* **Action**: Aligned input and target windows identically without a sequence offset index shift.
* **Maligned Objective**: The model learns a simple **Identity Function** (Autoencoding/Echoing).
* **Correct Objective**: The shifted model learns an **Autoregressive Transition Function** (Next-Token Dynamics).

## 🧪 Failure 3 — Optimizer Disabled
* **Action**: Commented out the `optimizer.step()` invocation while checking parameter matrices.
* **Observation**: Loss and gradients compute perfectly, but weight parameters stay completely stationary until `optimizer.step()` is restored, proving that gradient calculation alone does not update weights.


# Debugging Checklist

## Data

- [ ] Text is not empty.
- [ ] Vocabulary is valid.
- [ ] Input IDs are within vocabulary range.
- [ ] Input and target are shifted correctly.

## Model

- [ ] d_model is divisible by num_heads.
- [ ] Sequence length does not exceed max_sequence_length.
- [ ] Causal mask blocks future positions.
- [ ] Logit shape matches vocabulary size.

## Training

- [ ] Loss is finite.
- [ ] Gradients exist.
- [ ] Gradients are not all zero.
- [ ] Optimizer runs.
- [ ] Parameters change.

## Checkpoint

- [ ] Model state saves.
- [ ] Configuration saves.
- [ ] Vocabulary saves.
- [ ] Fresh model loads successfully.

## Generation

- [ ] Prompt encodes successfully.
- [ ] Model runs in evaluation mode.
- [ ] Next token is selected.
- [ ] Token is appended.
- [ ] Sequence respects context limits.