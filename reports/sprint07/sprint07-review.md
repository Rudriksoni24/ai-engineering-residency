# Sprint 7 Review — LoRA and Alignment

## Sprint Target

Adapt local models with parameter-efficient fine-tuning and understand modern alignment techniques.

## Sprint Outcome

Sprint 7 successfully progressed from fine-tuning fundamentals to a real local LoRA/PEFT adaptation and concluded with deterministic held-out evaluation.

The final integrated experiment used:

```text
Base model:
HuggingFaceTB/SmolLM2-135M-Instruct

Hardware:
Apple Silicon M2
16 GB RAM

Device:
MPS

LoRA:
rank 4
alpha 8
dropout 0.05

Targets:
q_proj
v_proj

Training:
30 steps
9 training examples

Validation:
3 held-out examples
```

Final Day 7 evaluation:

```text
Average base loss:     1.480352
Average adapted loss:  0.688470
Average delta:         -0.791881

Improved cases:        3 / 3
Regressed cases:       0
Overall improved:      True
```

This demonstrates successful local parameter-efficient adaptation on the small held-out evaluation set.

Qualitative generation remained imperfect, so the correct interpretation is improved target-response likelihood rather than production-ready schema compliance.

---

## Day 1 — Fine-Tuning Fundamentals

### Artifact

```text
Fine-Tuning Study Lab
```

### Learned

- forward pass
- loss calculation
- backpropagation
- optimizer updates
- trainable vs frozen parameters
- gradient and optimizer-state memory
- why full fine-tuning is expensive

### Core Insight

Full fine-tuning updates a very large portion of model parameters and therefore increases:

```text
gradient memory
+
optimizer-state memory
+
checkpoint size
+
training compute
```

This motivated parameter-efficient adaptation.

---

## Day 2 — LoRA Mathematics and Architecture

### Artifact

```text
LoRA Implementation
```

### Core Equation

```text
W' = W + ΔW

ΔW = BA
```

with:

```text
rank r << original matrix dimensions
```

### Implemented

- frozen base weights
- trainable LoRA A matrix
- trainable LoRA B matrix
- rank
- alpha/scaling
- zero-initialized adapter behavior
- trainable-parameter reduction
- merged vs unmerged behavior

### Core Insight

LoRA keeps the pretrained model as the shared base and learns a constrained low-rank update.

This drastically reduces trainable state without removing the base model's forward-pass cost.

---

## Day 3 — PEFT and Local Fine-Tuning

### Artifact

```text
Adapted Local Model
```

### Implemented

- Hugging Face pretrained causal LM
- PEFT `LoraConfig`
- `get_peft_model`
- target-module validation
- adapter-only local training
- adapter serialization
- fresh base-model reload
- `PeftModel.from_pretrained`
- before/after inference

### Core Insight

PEFT automates the adapter lifecycle, but the underlying mathematical concept remains:

```text
frozen W
+
trainable low-rank ΔW
```

The library does not replace understanding of the underlying adaptation method.

---

## Day 4 — Dataset Preparation for Fine-Tuning

### Artifact

```text
Training Dataset Pipeline
```

### Implemented

- instruction / input / response schema
- structural validation
- malformed-record rejection
- whitespace normalization
- canonical example identity
- SHA-256 IDs
- duplicate removal
- deterministic train/validation split
- exact normalized leakage detection
- instruction-style formatting
- chat-style formatting
- dataset statistics

### Core Insight

Training quality is bounded by data quality.

The correct preprocessing sequence is:

```text
raw data
↓
validate
↓
normalize
↓
deduplicate
↓
split
↓
leakage check
↓
format
```

Splitting before deduplication risks validation leakage.

---

## Day 5 — RLHF Concepts

### Artifact

```text
Alignment Architecture Notes
```

### Studied

```text
Base Model
   ↓
SFT
   ↓
Preference Data
   ↓
Reward Model
   ↓
RL Optimization / PPO
   ↓
Aligned Policy
```

### Covered

- chosen/rejected preferences
- human ranking
- reward models
- policy model
- reference model
- pairwise ranking loss
- PPO at a systems level
- KL control
- reward hacking
- alignment tax
- offline vs online preference feedback
- safety implications

### Core Insight

A reward model is a learned proxy for human preference, not a truth oracle.

A powerful optimizer can exploit weaknesses in that proxy, which is why reward hacking and policy/reference control matter.

---

## Day 6 — Direct Preference Optimization

### Artifact

```text
Preference Optimization Lab
```

### Implemented

```text
policy_margin
=
log πθ(chosen)
-
log πθ(rejected)
```

```text
reference_margin
=
log πref(chosen)
-
log πref(rejected)
```

```text
relative_margin
=
policy_margin
-
reference_margin
```

```text
DPO loss
=
-log sigmoid(
    beta × relative_margin
)
```

### Core Insight

DPO simplifies preference optimization by directly using chosen/rejected preference pairs instead of requiring a separately trained reward model and PPO loop in the basic formulation.

It does not remove:

- preference-data quality requirements
- reference-policy dependence
- evaluation needs
- safety risks
- bias risks

---

## Day 7 — Sprint Integration

### Artifact

```text
Domain-Adapted Local Model
```

### Integrated Architecture

```text
Synthetic Domain Data
       ↓
Validation / Normalization
       ↓
Deduplication
       ↓
Deterministic Split
       ↓
SmolLM2 Base Model
       ↓
PEFT LoRA
       ↓
Adapter Training
       ↓
Save / Reload
       ↓
Held-Out Completion Evaluation
```

### Dataset Results

```text
Raw examples:               14
Valid before deduplication: 13
Rejected:                    1
Duplicates removed:          1
Unique examples:            12
Training examples:           9
Validation examples:         3
```

Rejected record:

```text
index=13
reason=response cannot be empty
```

### Parameter Results

```text
Base model parameters:   134,515,008
Total PEFT parameters:   134,745,408
Trainable parameters:        230,400
Frozen parameters:       134,515,008
Trainable percentage:          0.1710%
```

This validated the parameter-efficiency objective of LoRA in a real pretrained model.

### Training Results

```text
First loss: 3.039624
Final loss: 1.980859
Training loss decreased: True
```

The loss fluctuated between steps but showed an overall downward trend.

### Held-Out Evaluation Results

#### Case `f17784291303`

```text
Base loss:     1.577631
Adapted loss:  0.837341
Delta:        -0.740290
Improved:      True
```

#### Case `7716df6af898`

```text
Base loss:     1.590683
Adapted loss:  0.828839
Delta:        -0.761844
Improved:      True
```

#### Case `2e78b49b531c`

```text
Base loss:     1.272741
Adapted loss:  0.399230
Delta:        -0.873510
Improved:      True
```

### Evaluation Summary

```text
Cases:                 3
Improved:              3
Regressed:             0
Unchanged:             0

Average base loss:     1.480352
Average adapted loss:  0.688470
Average delta:         -0.791881
Overall improved:      True
```

The average held-out completion loss fell by approximately 53.5%.

This is evidence that the adapter increased the likelihood of the expected domain responses on the small deterministic validation set.

### Qualitative Finding

The adapted model moved toward the requested structured output format, but generation still showed issues such as:

- incorrect field names
- incorrect enum/value normalization
- multiple JSON fragments instead of one complete object
- unsupported fields
- incomplete JSON
- extra response/error sections

Therefore Sprint 7 demonstrates successful adaptation, but not production-grade structured-output reliability.

---

# RAG vs LoRA vs Hybrid

## RAG

Use RAG primarily when the problem is:

```text
knowledge freshness
external knowledge
traceability
document grounding
citations
large changing knowledge stores
```

Examples:

- current policy manuals
- changing pricing
- latest regulations
- product documentation
- knowledge-base Q&A

### Strength

Knowledge can be updated without retraining model weights.

### Limitation

RAG does not fundamentally teach persistent model behavior.

---

## LoRA

Use LoRA primarily when the problem is:

```text
behavioral adaptation
output conventions
style
terminology
task-specific response patterns
```

Examples:

- mandatory JSON schema
- domain-specific language
- repeated classification format
- organization-specific response style

### Strength

Small adapter artifacts can specialize a shared base model.

### Limitation

LoRA is a poor primary mechanism for frequently changing factual knowledge.

---

## RAG + LoRA

Use both when the system requires:

```text
fresh knowledge
+
stable specialized behavior
```

Example:

```text
RAG:
retrieve latest payment-processing policy

LoRA:
produce the answer using the organization's fixed banking JSON schema
```

This separates responsibilities:

```text
retrieval owns knowledge freshness
adaptation owns behavioral conventions
```

---

# Sprint 7 Final Architectural Lesson

The question should not be:

```text
Should I use RAG or fine-tuning?
```

The better question is:

```text
What responsibility does this subsystem need to own?
```

If the problem is:

```text
changing information
```

prefer retrieval.

If the problem is:

```text
persistent behavior
```

consider LoRA/fine-tuning.

If both are required:

```text
RAG + LoRA
```

may provide the cleanest system boundary.

---

# Sprint 7 Exit Checklist

```text
✅ Explain why full fine-tuning is expensive.

✅ Explain low-rank adaptation.

✅ Train or adapt a local model using LoRA/PEFT.

✅ Prepare instruction data.

✅ Explain RLHF at a systems level.

✅ Explain reward models.

✅ Explain DPO.

✅ Compare LoRA adaptation with RAG.
```

---

# What Sprint 7 Successfully Proved

## 1. Fine-tuning mechanics are understood

The project moved from:

```text
forward
→ loss
→ backward
→ optimizer
```

to a real pretrained-language-model training loop.

## 2. LoRA mathematics are understood

The project implemented and validated:

```text
W' = W + BA
```

from first principles before using PEFT.

## 3. Parameter-efficient local adaptation works

The integrated run trained only:

```text
230,400 parameters
```

out of:

```text
134,745,408 total parameters
```

or:

```text
0.1710%
```

## 4. The adapter is reusable

The adapter was:

```text
trained
→ saved
→ model released
→ reloaded with fresh base
→ evaluated
```

successfully.

## 5. Data quality is part of model quality

The final run automatically removed:

```text
1 malformed example
1 duplicate example
```

before training.

## 6. Evaluation matters more than training loss

Training loss improved, but Sprint 7 also measured held-out response likelihood.

All three held-out cases improved in completion loss.

## 7. Qualitative evaluation still exposes weaknesses

Despite better completion loss, the model did not reliably produce the exact requested JSON schema.

This proves why one metric alone is insufficient.

---

# Main Remaining Technical Gap

The most obvious weakness after Sprint 7 is not whether LoRA works.

It does.

The bigger gap is:

```text
reliable structured-output compliance
```

The current adapter shows domain adaptation but still produces:

- malformed/incomplete JSON
- unexpected keys
- extra fields
- incorrect normalized values
- additional sections

A stronger next evaluation framework should measure:

```text
valid JSON rate
exact schema rate
required-field accuracy
enum accuracy
hallucinated-field rate
```

before considering deployment.

---

# Production Gaps

Sprint 7 deliberately did not solve:

- large-scale fine-tuning
- distributed training
- hyperparameter search
- quantization
- production RLHF
- production DPO
- large preference datasets
- production safety evaluation
- exact structured-output constraints
- adapter registry/versioning
- model serving
- online monitoring
- drift detection
- human evaluation pipelines

These are appropriate future productionization concerns rather than missing Day 7 requirements.

---

# Final Sprint 7 Result

Sprint 7 is technically complete once the full automated test and repository regression suite passes.

The integrated experiment demonstrates:

```text
clean training data
+
real PEFT LoRA adaptation
+
adapter persistence
+
held-out deterministic evaluation
+
evidence-based comparison
```

with measurable improvement on the small validation set.

The result should be described as:

> A successful resource-conscious local LoRA adaptation experiment with strong held-out completion-loss improvement, but with remaining structured-generation quality limitations that prevent production-readiness claims.
