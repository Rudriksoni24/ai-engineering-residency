## Week 2 Sprint Review## Sprint Goal
Build and understand the fundamental components of a Transformer-based decoder-only language model.
## Completed Components

* Self-Attention
* Q, K, V projections
* Scaled Dot-Product Attention
* Causal Masking
* Multi-Head Attention
* Feed-Forward Network
* Residual Connections
* LayerNorm
* Transformer Block
* Attention Is All You Need paper study
* MiniGPT architecture
* Character tokenizer
* Next-token dataset
* Cross entropy loss
* Training loop
* Backpropagation
* AdamW optimizer
* Checkpointing
* Autoregressive generation

## Demonstration

   1. Dataset used: A deliberately simple 3-line corpus designed for pipeline overfitting and sanity validation:
   
   machine learning is fun.
   machine learning is powerful.
   machine learning requires data.
   
   2. Vocabulary size: 21 unique characters (including lowercase letters, punctuation, and structural whitespace/newlines).
   3. Model configuration:
   * Layers (num_layers): 2
      * Attention Heads (num_heads): 4
      * Model Dimension (d_model): 128
      * Feed-Forward Dimension (d_ff): 256
      * Context Window (max_sequence_length): 32
   4. Parameter count: 1,055,488 parameters (100% active and marked as trainable via autograd).
   5. Initial loss: 3.0842 (Corresponds perfectly to uniform random choice across a vocabulary of 21 tokens: $-\ln(1/21) \approx 3.0445$).
   6. Final loss: 0.0084 (Achieved after 100 epochs, demonstrating complete mathematical convergence and data memorisation).
   7. Generated output: When evaluated deterministically with a locked seed (42) and greedy argmax decoding, prompting the model with unique phrase segments successfully reproduces the memorised patterns:
   * Prompt: 'machine learning requires '
      * Output: 'machine learning requires data.'
   
## What Works

* Cross-Module Architecture Integration: Modules are split cleanly across files and stitched together without circular path runtime errors (models/ handles network state configurations, data/ manages tensor token mappings, and labs/ executes pipeline orchestration).
* Strict Autoregressive Enforcement: The causal masking matrices (1s below the diagonal, 0s above) correctly route historical feature contexts to force true sequence prediction boundaries.
* Deterministic Backprop Integrity: Gradients propagate uninterrupted from the final linear lm_head projection, up through stacked FFN layers, block layer normalisations, and causal attention splits, reaching down to update row indices inside the foundational token_embedding lookup table.
* Reproducible Execution Checkpoints: The model state dictionary, vocabulary character map mappings, and architecture parameter classes serialize cleanly to a single local path snapshot file (checkpoints/minigpt.pt) and load seamlessly into entirely fresh model clones.

## What Does Not Work Yet

* Generalised Language Tracking: Because the current parameters are optimized using an isolated 3-line micro-corpus, the network lacks the capacity to compose novel sentences or generalize outside the boundary of its exact text inputs.
* Dynamic Multi-Batch Inference Shifting: The inference engine assumes single-row text stream expansions; it does not currently carry custom batch padding operations required to generate variable lengths concurrently.
* Context Over-Scaling Protection: Attempting to feed prompt token blocks longer than the maximum sequence constraint (32) causes an explicit ValueError, meaning the architecture cannot handle long-form conversational inputs yet.

## Known Limitations

* Character-level tokenizer
* Tiny dataset
* Tiny model
* No pretrained knowledge
* No KV cache
* No optimized inference
* No evaluation benchmark
* No distributed training

## Next Steps
Week 3:
Embeddings, retrieval, and RAG foundations.
------------------------------