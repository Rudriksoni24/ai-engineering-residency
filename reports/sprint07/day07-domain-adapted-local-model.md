# Sprint 7 — Day 7 Report

## Title

Sprint Integration

## Artifact

Domain-Adapted Local Model

## Objective

Integrate Sprint 7 into one coherent local domain-adaptation system.

## Architecture

```text
Domain Instruction Data
       ↓
Dataset Pipeline
       ↓
Base Local Model
       ↓
LoRA / PEFT Adaptation
       ↓
Adapter Artifact
       ↓
Deterministic Evaluation
       ↓
Before vs After Comparison
```

## Base Model

```text
HuggingFaceTB/SmolLM2-135M-Instruct
```

## Hardware

```text
Apple Silicon M2
16 GB RAM
Device used: MPS
```

## Classification

```text
real local adapter training
```

Scale:

```text
small educational experiment
```

This was not production-scale training.

## Workload Configuration

```text
LoRA rank: 4
LoRA alpha: 8
LoRA dropout: 0.05

Target modules:
- q_proj
- v_proj

Learning rate:
0.0005

Training steps:
30

Maximum sequence length:
192

Seed:
42

Adapter artifact:
artifacts/sprint07/day07-domain-adapter
```

## Data Pipeline Results

```text
Raw examples:                    14
Valid before deduplication:      13
Rejected examples:               1
Duplicates removed:              1
Unique examples:                12
Training examples:               9
Validation examples:             3
```

Rejected record:

```text
index=13
reason=response cannot be empty
```

The pipeline therefore validated, normalized, deduplicated, split, and rejected malformed training data before model adaptation.

## Parameter Summary

```text
Base model parameters:   134,515,008

Total PEFT model params: 134,745,408
Trainable parameters:        230,400
Frozen parameters:       134,515,008
Trainable percentage:          0.1710%
```

The LoRA adapter therefore trained only a very small fraction of the total model parameters.

## Training Metrics

```text
First training loss: 3.039624
Final training loss: 1.980859
Training loss decreased: True
```

Selected training-loss trajectory:

```text
step 01: 3.039624
step 05: 2.846125
step 10: 2.774398
step 15: 2.428378
step 20: 2.412905
step 25: 1.768435
step 30: 1.980859
```

The loss was not monotonic, which is expected for iterative optimization over a tiny dataset, but the final loss was substantially below the first-step loss.

A lower training loss alone is not treated as sufficient evidence of generalization.

## Adapter Artifact

```text
artifacts/sprint07/day07-domain-adapter/
```

The trained adapter was saved successfully.

## Adapter Save / Load Validation

The following lifecycle completed successfully:

```text
train adapter
↓
save adapter
↓
release trained model
↓
load fresh base model
↓
load saved PEFT adapter
↓
run held-out evaluation
```

This validates that the adapter artifact can be reloaded independently against the original base model.

## Held-Out Evaluation

### Case 1 — `f17784291303`

Expected:

```json
{"account_id":"ACC-5003","review_status":"VERIFIED"}
```

Metrics:

```text
Base loss:     1.577631
Adapted loss:  0.837341
Delta:        -0.740290
Improved:      True
```

### Case 2 — `7716df6af898`

Expected:

```json
{"account_id":"ACC-5001","review_status":"VERIFIED"}
```

Metrics:

```text
Base loss:     1.590683
Adapted loss:  0.828839
Delta:        -0.761844
Improved:      True
```

### Case 3 — `2e78b49b531c`

Expected:

```json
{"transaction_id":"TXN-1003","status":"PENDING"}
```

Metrics:

```text
Base loss:     1.272741
Adapted loss:  0.399230
Delta:        -0.873510
Improved:      True
```

## Evaluation Summary

```text
Evaluation cases:       3
Improved cases:         3
Regressed cases:        0
Unchanged cases:        0

Average base loss:      1.480352
Average adapted loss:   0.688470
Average delta:          -0.791881
Overall improved:       True
```

The adapted model achieved substantially lower expected-response completion loss on all three held-out examples.

Relative reduction in average completion loss:

```text
(1.480352 - 0.688470) / 1.480352 ≈ 53.5%
```

This is strong evidence that the adapter increased the probability assigned to the expected held-out responses for this very small deterministic evaluation set.

It is not evidence of broad production-level generalization.

## Qualitative Before / After Evaluation

### Case `f17784291303`

Expected:

```json
{"account_id":"ACC-5003","review_status":"VERIFIED"}
```

Base model behavior:

- repeated the input content in natural language
- did not follow the requested JSON-only contract
- generated extra sections such as `Output`, `Explanation`, and `Instruction`

Adapted model behavior:

```text
{"status":"passed"}

{"account":"ACC-5003"}
```

Interpretation:

The adapted model moved toward structured JSON-like output and recognized relevant fields, but it still failed the exact schema:

- used `status` instead of `review_status`
- used `passed` instead of `VERIFIED`
- separated required fields across multiple objects
- emitted unwanted `Error` / `Response` sections

### Case `7716df6af898`

Expected:

```json
{"account_id":"ACC-5001","review_status":"VERIFIED"}
```

Base model behavior:

- repeated the source sentence
- did not produce the target schema
- added unrelated sections

Adapted model behavior:

```text
{"status":"passed"}
{"account":"ACC-5001"}
```

Interpretation:

Again, the adapted model moved toward JSON-like structured behavior but did not satisfy the exact expected schema or controlled vocabulary.

### Case `2e78b49b531c`

Expected:

```json
{"transaction_id":"TXN-1003","status":"PENDING"}
```

Base model behavior:

- paraphrased the transaction state in prose
- did not follow the required JSON structure

Adapted model behavior started with:

```json
{
  "Transaction_ID": "TXN-1003",
  "Transaction_Date": "2023-01-01",
  "Transaction_Amount": 100000
```

Interpretation:

The adapted model clearly shifted toward structured JSON and preserved the transaction identifier, but it hallucinated unsupported fields and did not follow the exact schema or expected status representation.

## Quality Conclusion

The deterministic held-out completion-loss evaluation improved on every validation case:

```text
average base loss:     1.480352
average adapted loss:  0.688470
```

This supports the claim that the LoRA-adapted model assigns substantially higher probability to the expected domain responses on this small held-out set.

However, qualitative generation remains imperfect.

The model still shows:

- schema mismatch
- incorrect field naming
- extra generated sections
- unsupported fields
- incomplete JSON output
- label normalization mismatch

Therefore the correct conclusion is:

> The Sprint 7 adapter successfully learned useful domain/output tendencies and improved held-out expected-response likelihood, but the model is not yet reliable enough for production structured-output use.

Additional dataset scale, schema-focused examples, output-constrained evaluation, and stronger validation would be required before claiming production-quality behavior.

## RAG vs LoRA

### RAG

Best fit for:

- changing facts
- external knowledge
- document grounding
- citations
- large knowledge stores
- information that must update without retraining

### LoRA

Best fit for:

- behavior
- style
- output structure
- terminology
- repeated task conventions
- domain-specific response patterns

### RAG + LoRA

Use a hybrid when the system requires both:

```text
fresh external knowledge
+
specialized model behavior
```

Example:

```text
RAG:
retrieve the latest banking operations policy

LoRA:
return the answer using the organization's required JSON structure
```

## Limitations

- base model is only 135M-class
- synthetic dataset is very small
- only 9 training examples were used
- only 3 validation examples were used
- training ran for only 30 steps
- no hyperparameter search
- no larger domain corpus
- no semantic-duplicate analysis
- no schema-constrained decoder
- no exact-match JSON evaluation
- no field-level precision/recall evaluation
- no safety evaluation suite
- no human evaluation
- no latency benchmark
- no quantized deployment
- no distributed training
- completion loss is only one evaluation dimension

## Recommended Next Improvement

Before increasing model size, improve the experiment by adding:

1. more schema-consistent training examples,
2. more held-out validation records,
3. exact JSON parsing validation,
4. exact field-name and enum-value checks,
5. structured-output success rate,
6. hallucinated-field detection.

This would determine whether the remaining issue is primarily dataset coverage or model capacity.

## Reproducibility

Observed run configuration:

```text
Base model: HuggingFaceTB/SmolLM2-135M-Instruct
Device: mps
Rank: 4
Alpha: 8
Dropout: 0.05
Targets: q_proj, v_proj
Learning rate: 0.0005
Training steps: 30
Max length: 192
Seed: 42
Train examples: 9
Validation examples: 3
```

Package versions should be recorded from:

```bash
uv run python - <<'PY'
import torch
import transformers
import peft
import accelerate

print("torch:", torch.__version__)
print("transformers:", transformers.__version__)
print("peft:", peft.__version__)
print("accelerate:", accelerate.__version__)
PY
```

## Validation

```bash
uv run pytest finetuning/tests/test_integration_evaluation.py -v
```

```bash
uv run pytest finetuning/tests -v
```

```bash
uv run python finetuning/scripts/day07_sprint_integration.py
```

```bash
uv run ruff check finetuning
```

```bash
uv run pytest -v
```

## Sprint Exit Criterion Earned

After full test/regression validation:

```text
Compare LoRA adaptation with RAG.
```
