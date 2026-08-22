## Attention Is All You Need — Code Mapping## 1. Positional Encoding
Repository implementation:
labs/transformers/positional-encoding/positional_encoding.py
Paper concept:
Since our Transformer processes all tokens simultaneously, it has no native concept of word order. Positional encodings add fixed, unique sine and cosine wave frequencies directly to the token embeddings. This gives every token a distinct mathematical address showing its exact position and distance along the sequence timeline without using loops.
Input shape:
(batch_size, sequence_length, d_model) — Raw token embeddings.
Output shape:
(batch_size, sequence_length, d_model) — Embeddings with order tracking baked in (embeddings + positional_encodings).
------------------------------
## 2. Scaled Dot-Product Attention
Repository implementation:
Integrated inside your labs/transformers/multi-head-attention/multi_head_attention.py script.
Paper equation:
$$Attention(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$ 
Implementation mapping:

* Q → Generated via self.Wq(x) and split into shape (batch, num_heads, seq_len, head_dim).
* K → Generated via self.Wk(x) and split into shape (batch, num_heads, seq_len, head_dim).
* V → Generated via self.Wv(x) and split into shape (batch, num_heads, seq_len, head_dim).
* Scores → Calculated via torch.matmul(Q, K.transpose(-2, -1)) to get a (batch, num_heads, seq_len, seq_len) relational grid.
* Scaling → Divided by math.sqrt(self.head_dim) to keep scores small and prevent vanishing gradients before softmax.
* Softmax → Handled by your custom, numerically stable function: self._stable_softmax(scores, dim=-1).
* Weighted values → Computed via torch.matmul(weights, V) to extract a weighted percentage of the semantic data.

------------------------------
## 3. Multi-Head Attention
Repository implementation:
Located in labs/transformers/multi-head-attention/multi_head_attention.py under the MultiHeadAttention class.
Paper equation:
$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h)W^O$$ 
Mapping:

* Head Splitting → Achieved by reshaping with .view(batch, seq_len, num_heads, head_dim) and moving the heads forward using .transpose(1, 2).
* Concatenation (Concat) → Reversed using .transpose(1, 2).contiguous() and flattening the channels back to (batch, seq_len, d_model) via .view().
* Output Projection Layer ($W^O$) → Handled directly by your learnable mixer matrix: self.Wo(concat_out).

------------------------------
## 4. Transformer Block
Repository implementation:
labs/transformers/transformer-block/transformer_block.py under the TransformerBlock class.
Architecture:

Multi-Head Attention
    ↓
Add + Norm (Post-LayerNorm 1)
    ↓
Feed Forward
    ↓
Add + Norm (Post-LayerNorm 2)

Mapping:

* Multi-Head Attention → Executed via attn_out, _ = self.mha(x, mask=mask).
* Causal Mask Integration → Dynamically intercepts mask="causal" strings using your verified utility imported directly from labs/transformers/self-attention/attention.py.
* First Add + Norm → Handled by residual_1 = x + self.dropout(attn_out) followed by self.norm1(residual_1).
* Feed Forward → Executed via ffn_out = self.ffn(x) using the internal w_1 and w_2 layers of your FeedForwardNetwork.
* Second Add + Norm → Handled by residual_2 = x + self.dropout(ffn_out) followed by self.norm2(residual_2).

------------------------------
## What Is Missing?## Required before MiniGPT

* Tokenizer: A small parser to break raw input strings down into individual character or sub-word integer tokens.
* Token vocabulary: A mapped directory linking text units to fixed vector indices.
* Decoder-only stack: A global module class to wrap and chain multiple TransformerBlock objects back-to-back.
* Language model output head: A final projection layer (nn.Linear(d_model, vocab_size)) to turn block vectors into logit probabilities across your vocabulary.
* Loss function: A standard Cross-Entropy loss criterion to score predictions during updates.
* Training loop & Dataset: A script handling optimizer steps (optimizer.step()), batch generation, and text file data processing.
* Text generation routine: An inference function using sampling methods (like Top-k or temperature) to generate text autoregressively.

## Not Required for the First MiniGPT

* Full encoder stack (Bypassed — Decoder-only GPT models do not need an Encoder)
* Cross-attention (Bypassed — No Encoder representations to fuse against)
* Encoder-decoder Transformer (Bypassed — We are building a generative causal model instead of an explicit translation pipeline)