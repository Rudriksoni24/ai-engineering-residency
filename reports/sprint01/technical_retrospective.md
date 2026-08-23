## Week 2 Technical Retrospective## What I Understand Well

   1. Autoregressive Sequence Shifting: How the input sequence ($X$) and target sequence ($Y$) must be perfectly offset by exactly one token slot ($Y_t = X_{t+1}$) to structurally enforce next-token prediction mechanics inside the data pipeline.
   2. Causal Masking and Attention Isolation: The mathematical application of a lower-triangular matrix filled with $-\infty$ values prior to the softmax operation, ensuring that token representations at index $i$ cannot access feature info at index $j$ where $j > i$.
   3. The Loss Reshape Contract: Why a 3D matrix output shape of (batch, sequence, vocab_size) must be collapsed into a 2D matrix shape of (batch × sequence, vocab_size) to align with a flattened 1D index target tensor for standard PyTorch Cross-Entropy calculations.

## Concepts I Can Explain But Not Yet Implement Confidently

   1. Dynamic Key-Value (KV) Caching: Storing historic token key and value vectors during step-by-step decoding loops to eliminate redundant $O(T^3)$ attention matrix recomputations across growing prompt windows.
   2. Advanced Sub-word Tokenization Mechanics: The code-level optimization required to merge frequent character pairs iteratively (like Byte-Pair Encoding) to build dynamic token vocabularies that handle massive external text corpora efficiently.
   3. Advanced Sampling Decoding Configurations: Structuring random multinomial sampling models utilizing temperature scaling arrays and top-$k$/top-$p$ probabilistic filter boundaries to stop greedy decoding loops without breaking token semantic paths.

## Bugs I Encountered

| Bug | Root Cause | Fix | Prevention |
|---|---|---|---|
| TypeError: MultiHeadAttention.forward() got multiple values... | The block passed three positional variables (x, x, x) into an attention function that only expected a single combined sequence tensor (x). | Modified line 75 of transformer_block.py to pass the tensor parameter explicitly: self.mha(x, mask=mask). | Always match internal layer forward signatures exactly when writing wrapper or parent container execution blocks. |
| TypeError: masked_fill() received an invalid combination... | Passing the string literal "causal" deep into the MHA inner layers caused mask == 0 to evaluate to a raw Python boolean False instead of a true PyTorch Tensor. | Upgraded the master block wrapper to capture "causal" early and generate a real torch.Tensor on the proper device before passing it downstream. | Keep string-parsing logic in outer wrapper modules and enforce strict tensor tracking types inside raw mathematical sub-layers. |
| TypeError: cannot use 'list' as a dict key (unhashable type) | current_tokens.tolist() was executed on a 2D tensor, outputting a nested Python array [[...]] with a batch dimension that the character dictionary could not hash. | Extracted the primary batch row explicitly using indexing: tokenizer.decode(current_tokens.tolist()[0]). | Always check tensor row depths when transitioning back and forth between high-dimensional model graphs and flat text structures. |

## Architecture Decisions

   1. Why decoder-only?
   Because the objective of MiniGPT is autoregressive text generation. Discarding the entire encoder stack and all cross-attention components streamlines the network, optimizing every layer exclusively to learn how text patterns continuously expand forward based on historic context windows.
   2. Why causal masking?
   Without a causal mask, bidirectional attention lets tokens look ahead and cheat by reading upcoming target tokens sitting at position $t+1$. The causal mask simulates real-world production conditions during parallel training, forcing the model to calculate predictions using historical text context only.
   3. Why character tokenizer for this lab?
   It strips out tokenization complexity (like BPE segmentation rules and vocabulary maps with over 50,000 entries). Keeping a tiny vocabulary of roughly 20-30 characters keeps the lm_head extremely lightweight, makes text-to-tensor steps clear, and helps isolate shape bugs instantly.
   4. Why overfit a tiny dataset first?
   It is a critical pipeline sanity check. If a neural network model cannot successfully minimize its loss and memorize a simple 3-line text string with dropout disabled, it means there is a fatal bug in the gradient paths, masking matrices, or weight shapes. Finding these bugs on a tiny string saves hours of wasted cluster training time.

## Biggest Misconceptions Corrected

   1. Attention is Not Feature Processing: I realized that the attention mechanism does not transform token meanings on its own. It is simply a context-routing traffic cop that shifts and mixes existing vectors across space. The heavy feature transformations happen vertically inside the position-wise Feed-Forward Network.
   2. Supervised Loss vs Self-Supervised Targets: I corrected my understanding of labels. Even though we use supervised CrossEntropyLoss with strict target arrays, the process is self-supervised. An automated script creates the data-target splits natively from raw text streams without any human annotators.
   3. Training Parallelism is an Illusion at Inference: I discovered that the massive speed of parallel training is only possible because the entire sentence is already known. During real-world generation, the future is unknown, forcing the model to step forward sequentially, one token at a time.

## Questions Before Week 3

   1. When scaling up from characters to a sub-word BPE tokenizer, how do we determine the perfect mathematical sweet-spot for vocabulary size to balance embedding memory footprints against sequencing speed?
   2. How do learnable layer normalization weights ($\gamma$ and $\beta$) physically interact with the scaling properties of the residual stream when stacking models deeper than 12 layers?
   3. What is the standard programmatic pattern for managing variable-length batch sequences using padding tokens without letting the attention engine read garbage pad data during cross-batch loss processing?

------------------------------