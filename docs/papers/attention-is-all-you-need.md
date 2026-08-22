## Attention Is All You Need
Paper:
https://arxiv.org/abs/1706.03762
## Problem Being Solved
Write in your own words:
Why were recurrent architectures a limitation for sequence modeling?
Recurrent architectures like RNNs, LSTMs, and GRUs process text sequentially, one word at a time. To understand word 10, the model must first process words 1 through 9 in order. This creates two massive bottlenecks. First, it prevents parallel training because computations cannot happen simultaneously across a whole sentence, making training incredibly slow on large datasets. Second, they struggle with long-range dependencies. By the time a recurrent model reaches the end of a long paragraph, the mathematical signal from the first sentence has been multiplied so many times that it either vanishes to zero or explodes, causing the model to literally forget how the sentence started.
------------------------------
## Core Idea
The Transformer replaces recurrence with attention mechanisms.
My explanation:
The core idea of the Transformer is to completely drop loops and recurrence, allowing every word in a sentence to look at and talk to every other word at the exact same time. Instead of step-by-step sequential processing, the entire sentence is processed in parallel. It uses a mathematical routing system called attention to let words dynamically determine which other words are most relevant to them, regardless of how far apart they sit in the text. For example, in the sentence "The bank approved the loan because it had low risk," the word "it" can instantly connect to "loan" in a single computational step, rather than climbing through an intermediate chain of words.
------------------------------
## Scaled Dot-Product Attention
Formula:
Attention(Q, K, V) =
softmax(QKᵀ / √dₖ)V
## Query
The Query (Q) represents what a word is currently searching for or trying to understand. Think of it like a search query you type into Google. For example, if the model is processing the word "bank" in "The bank approved the loan," the Query vector for "bank" acts as a question asking: "What kind of bank am I, and who or what interacts with me?"
## Key
The Key (K) acts like a label or index attached to every word in the sentence. It represents what kind of information that word can offer to any searching Query. Returning to the Google search analogy, Keys are like the titles and descriptions of web pages. The word "approved" has a Key indicating it is an action performed by a financial institution, which perfectly matches what the Query for "bank" is hunting for.
## Value
The Value (V) is the actual semantic content or meaning stored inside each word. Once a Query multiplies with a Key to determine how much attention they should pay to each other, that score is used to extract a weighted percentage of the corresponding Value. If the Query for "bank" matches strongly with the Key for "approved," the model extracts the financial meaning from the Value vector of "approved" and blends it back into the representation for "bank."
## Why Scale by √dₖ?
When the size of the vectors (the dimension $d_k$) becomes very large, the dot products between Queries and Keys grow to massive numerical values. When you feed these massive numbers into a softmax function, the gradients become extremely flat and close to zero. This leads to the vanishing gradient problem, which completely stalls neural network training. Dividing by the square root of the head dimension ($\sqrt{d_k}$) scales the variance back down to 1.0, keeping the numbers small and ensuring that gradients flow cleanly during backpropagation.
------------------------------
## Multi-Head Attention
Formula:
MultiHead(Q, K, V) =
Concat(head₁, ..., headₕ)Wᴼ
## Why Multiple Heads?
If you only use a single attention mechanism, all words are forced to compromise on one averaged relationship at a time. Multi-head attention allows the model to split its feature vectors into smaller sub-dimensions so it can look at the text through multiple independent viewpoints simultaneously. This prevents different linguistic relationships from blocking or muddying one another.
## What Each Head Represents
Each head represents a unique contextual lens or specialized linguistic tracker. For example, in the phrase "The bank approved the loan," Head 1 might focus purely on grammar rules (connecting the noun "bank" to its verb "approved"). Head 2 might track semantic relationships (connecting "bank" to "loan" to determine it is a financial institution, not a riverbank). Head 3 might track relative positions (focusing on the word immediately preceding or following).
------------------------------
## Encoder
The Encoder is a stack of identical blocks designed to read an input sequence and build a rich, context-aware map of information. It takes raw word embeddings, adds positional tracking, and passes them through multi-head attention and feed-forward networks. The output of the final encoder block is not a single prediction, but a matrix of highly informative vectors where every word's representation has been updated to reflect the full context of the entire surrounding sentence.
------------------------------
## Decoder
The Decoder is a stack of blocks designed to generate an output sequence autoregressively, predicting one token at a time. It works by taking the context map produced by the Encoder and using it alongside its own past predictions to generate the next word. Unlike the Encoder, which looks at the whole sequence simultaneously, the Decoder must generate text step-by-step, ensuring it never previews words that it is supposed to be predicting in the future.
------------------------------
## Masked Self-Attention
Masked Self-Attention is a variation used exclusively within the Decoder to prevent it from cheating during training. When training a model to predict the next word, it has access to the full correct sentence. To simulate a real-world scenario where the future is unknown, an upper-triangular matrix filled with $-\infty$ is added to the attention scores before the softmax operation. This zeros out the attention weights for all future positions. For example, when generating the third word in a sentence, the mask ensures the model can only look at words 1 and 2, completely blocking it from looking at words 4 or 5.
------------------------------
## Cross-Attention
Cross-Attention is the structural bridge that links the Encoder and the Decoder together. In this layer, the Queries (Q) come from the Decoder's current generation progress, while the Keys (K) and Values (V) come directly from the final output map of the Encoder. This allows the Decoder to look back at the original input sequence before making a prediction. For example, in a machine translation task, as the decoder generates French words, cross-attention allows it to look back at the English encoder map to find the exact noun or verb it needs to translate next.
------------------------------
## Feed-Forward Network
The Feed-Forward Network (FFN) is a position-wise processing block that sits immediately after the attention layer in every Transformer block. While attention is designed to communicate and route data across tokens horizontally, the FFN processes each token vector vertically and completely in isolation. It expands the tensor into a wider hidden space (from 512 dimensions to 2048) where features become linearly separable, applies a non-linear activation function (like ReLU), and compresses it back down. This serves as a localized computation engine to synthesize new features from the relationships mapped by the attention layer.
------------------------------
## Residual Connections
Residual Connections are identity shortcuts that pass the input of a sub-layer around the processing block and add it directly to the sub-layer's output ($x + \text{Sublayer}(x)$). This structure breaks up the complex non-linear multiplication paths within deep networks, creating an uninterrupted linear highway. It allows raw token representations to be preserved deep into the network without being corrupted by poor layer initializations, and ensures that training gradients can backpropagate directly back to early layers without vanishing.
------------------------------
## Layer Normalization
Layer Normalization is a stabilization technique that rescales neural network activations. It operates across the feature dimension ($d_{model}$) for each individual token independently, forcing the values to maintain a mean of 0.0 and a variance of 1.0. By continuously resetting the scale of activations at the end of every sub-layer, it prevents internal values from growing uncontrollably or collapsing to zero as depth increases. This statistical control makes training fast, robust, and highly predictable.
------------------------------
## Positional Encoding
Because the Transformer processes all tokens in parallel using permutation-invariant matrix multiplication, it has no native concept of word order. To the raw attention math, the phrase "cats eat fish" looks exactly like "fish eat cats." To fix this, Positional Encodings are fixed vectors generated using sine and cosine waves of different frequencies. These vectors are added directly to the initial token embeddings. They inject a unique mathematical signature that tells the model exactly where each word sits in the timeline, allowing it to track sequence order and distance without using loops.
------------------------------
## Original Transformer vs GPT
The original architecture proposed in the 2017 paper is an Encoder-Decoder model, explicitly designed for sequence-to-sequence tasks like language translation. It passes text into an encoder stack to build a complete context map, then routes that map to a decoder stack to generate a target sequence.
GPT (Generative Pre-trained Transformer) is a Decoder-only architecture. It completely discards the Encoder stack and the Cross-Attention layers. It processes text strictly using a stack of Masked Self-Attention and Feed-Forward layers, optimizing it entirely for generative language modeling, where the sole task is predicting the single next token given a historic text prompt.
------------------------------
## My Biggest Insights

   1. Routing and Processing are Separated: Attention does not actually process or transform information; it is simply a dynamic routing matrix that brings relevant vectors into the same space. The heavy processing and feature synthesis are handled independently by the Feed-Forward Networks.
   2. Matrix Multiplications Replace Time Steps: The Transformer transforms a time-dependent sequential problem into a pure space-dependent geometry problem. By swapping out temporal loops for static matrix operations, sequence modeling can scale exponentially alongside modern hardware parallelism.
   3. Residual Networks Protect Information Identity: Identity connections prevent representations from collapsing or drifting as they climb deep through a model. They guarantee that the fundamental definition of a word is not wiped out by downstream transformations.

------------------------------
## Questions I Still Have

   1. How do we determine the optimal ratio between $d_{model}$ and $d_{ff}$ when scaling up models beyond standard configurations?
   2. At what exact sequence length does the quadratic compute cost ($O(N^2)$) of vanilla dot-product self-attention become less efficient than state-space or recurrent approximations?
   3. How do the learnable affine parameters ($\gamma$ and $\beta$) inside Post-LayerNorm structures dynamically alter the scale of the residual stream during early training phases compared to Pre-LayerNorm layouts?


