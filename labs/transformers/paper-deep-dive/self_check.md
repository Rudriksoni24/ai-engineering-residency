## Self Check — Attention Is All You Need
Answer these without reading your notes first.
## Question 1
Why did the Transformer architecture remove recurrence?
Answer:
Recurrence (like RNNs, LSTMs) forces the model to process tokens sequentially, one step at a time. This creates an architectural bottleneck because you cannot compute a word until the previous word is finished, preventing massive GPU parallelization. Removing recurrence allows the entire sentence to be processed at once, drastically accelerating training speeds while eliminating the problem of vanishing or exploding gradients over long distances.
------------------------------
## Question 2
Why is attention divided by $\sqrt{d_k}$?
Answer:
When the head dimension ($d_k$) becomes large, the dot products between Queries and Keys can grow to very large magnitudes. Feeding these massive numbers into the softmax function results in extremely small gradients (the function flattens out). This stalls neural network training due to vanishing gradients. Dividing by $\sqrt{d_k}$ rescales the variance back down to 1.0, keeping the softmax distributions stable and the gradients active.
------------------------------
## Question 3
Why does the decoder need causal masking?
Answer:
The decoder's primary task is autoregressive generation—predicting the next token given only the past text history. During training, the entire target sentence is fed into the model at once. Without a causal mask, the attention mechanism would cheat by looking ahead at tokens that appear later in the sequence. The causal mask zeroes out future information, forcing the model to learn to predict under real-world constraints.
------------------------------
## Question 4
Why doesn't the encoder use causal masking?
Answer:
The encoder's job is to build a rich, bidirectional context map of the input sequence. For tasks like reading a source sentence before translation, there is no risk of "cheating." Allowing tokens to look at both preceding and subsequent words simultaneously (e.g., "bank" looking at both "river" or "loan" nearby) helps the encoder build a much more precise and well-rounded understanding of the sentence semantics.
------------------------------
## Question 5
What is the difference between self-attention and cross-attention?
Answer:

* Self-Attention: The Queries (Q), Keys (K), and Values (V) all originate from the exact same input source tensor (within the same layer). It allows a single sequence to map out internal relationships within itself.
* Cross-Attention: The Queries (Q) come from the decoder's current progress, while the Keys (K) and Values (V) come from the final output context matrix of the encoder. It serves as a bridge allowing the decoder to reference the original input text.

------------------------------
## Question 6
Why is positional information necessary?
Answer:
Because the attention mechanism relies purely on set-based matrix multiplications, it is entirely permutation-invariant. Without positional context, the raw attention math treats "cats eat fish" and "fish eat cats" as completely identical configurations. Positional information must be manually added to the initial token embeddings to inject a spatial signature so the model can track token order and sequence layout.
------------------------------
## Question 7
What unique role does the FFN play?
Answer:
While attention acts as a horizontal context-routing layer that moves information between tokens, it only computes linear weighted combinations. The FFN acts as the vertical processing engine. By expanding vectors into a 4x wider hidden space and applying a non-linear activation (like ReLU), it synthesizes new features, runs deep localized logic, and stores abstract key-value knowledge about the contextualized tokens.
------------------------------
## Question 8
What do residual connections contribute?
Answer:
Residual connections create an unbroken linear identity highway through the deep network stack. They decouple information transmission from feature extraction, preventing deep layers from overwriting or destroying vital early token properties. Crucially, they keep a direct mathematical backpropagation pathway open, preventing gradients from vanishing or breaking through hundreds of sequential parameters.
------------------------------
## Question 9
Why is the original Transformer different from GPT?
Answer:
The original Transformer is an Encoder-Decoder architecture built for translation or sequence transduction—mapping an input text sequence directly into an output sequence. GPT (Generative Pre-trained Transformer) is a Decoder-only architecture. It discards the entire encoder stack and all cross-attention layers, focusing exclusively on a single masked self-attention pipeline optimized for predicting the next token.
------------------------------
## Question 10
What must still be built before training MiniGPT?
Answer:
Before training MiniGPT, you need to build: a character or sub-word Tokenizer to convert strings into integer streams, a fixed Token Vocabulary map, a Multi-Layer Decoder Stack to chain your custom TransformerBlock blocks sequentially, a Language Model Head (nn.Linear) to project your model states into vocabulary logits, a standard Cross-Entropy Loss Function, a functional Training Loop with a dataset loader, and an autoregressive Text Generation Routine (using temperature or Top-k sampling) to run inference.

