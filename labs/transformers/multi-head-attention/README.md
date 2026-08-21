# Multi-Head Attention Shape Tracing
Multi-Head Attention Tensor Shape TracingTo process multiple attention calculations in parallel, the high-dimensional workspace must be split across independent structural heads. This process tracks a single batch sequence through the complete transformation loop.1. Setup Parametersbatch_size (\(B\)) = 1 (Number of parallel sequences processed)sequence_length (\(T\)) = 4 (Number of text tokens in our sequence)d_model (\(D\)) = 8 (Total hidden feature dimensions per token)num_heads (\(H\)) = 2 (Number of parallel attention channels)\(\text{head\_dimension}\ (d_{k})=\frac{d\_model}{num\_heads}=\frac{8}{2}=4\)
2. Pipeline Shape Transformations
       Input Tensor (X)
         Shape: (1, 4, 8)  →  [batch_size, sequence_length, d_model]
                │
                ▼
  Linear Projections (W_q, W_k, W_v)
         Shape: (1, 4, 8)
                │
                ▼
     Reshape & Transpose (Heads Split)
         Shape: (1, 2, 4, 4)  →  [batch_size, num_heads, sequence_length, head_dimension]
                │
                ▼
     Scaled Dot-Product Attention
         Scores Matrix Weight: (1, 2, 4, 4)  →  [batch_size, num_heads, seq_len, seq_len]
         Output Context Heads: (1, 2, 4, 4)  →  [batch_size, num_heads, sequence_length, head_dimension]
                │
                ▼
     Transpose & Reshape (Concatenation)
         Shape: (1, 4, 8)  →  [batch_size, sequence_length, num_heads * head_dimension]
                │
                ▼
      Final Output Projection (W_o)
         Shape: (1, 4, 8)  →  [batch_size, sequence_length, d_model]

3. Core Architectural RulesThe Head Separation Split: The tensor is initially projected to a shape of (batch_size, sequence_length, num_heads, head_dimension). It must then be transposed using .transpose(1, 2) to achieve the final shape of (batch_size, num_heads, sequence_length, head_dimension) [INDEX]. This moves the num_heads axis to dimension 1, allowing PyTorch to perform batch matrix multiplications across all heads simultaneously [INDEX].The Output Convergence: After calculating attention independently for each head, the tensors are combined by switching the dimensions back with .transpose(1, 2) and calling .reshape(batch_size, sequence_length, d_model). This merges the separate head perspectives into a unified token matrix without destroying positional layout.



1. Why not just increase d_model instead of adding heads?Increasing d_model only makes the vectors wider. If you keep a single head, it can still only compute one type of relationship at a time across the entire sequence. For example, a word might need to hook into its subject, its verb, and its pronoun modifier simultaneously. A single larger head will average these relationships together, muddying the signal. Adding heads adds different channels of focus without blowing up parameters.2. What does this mean: "Different heads attend to different representation subspaces"?This means each head looks at the text through a unique lens. Think of a sentence like a movie scene.Head 1 might focus entirely on tracking syntax (e.g., matching verbs to nouns).Head 2 might track positional context (e.g., looking at the immediately preceding word).Head 3 might track semantic logic (e.g., connecting "bank" to "loan" instead of a riverbank).By projecting data into smaller "subspaces," the model can execute multiple independent logical searches simultaneously.3. Why does each head use head_dim = d_model / num_heads instead of the full d_model?To keep the computational cost and parameter count identical to a single-head model. If every head used the full d_model, running 8 heads would make the model 8 times more expensive to calculate and train. Slicing the dimension ensures that multi-head attention is purely an architectural reorganization of the same raw compute power.4. Why do attention weights have the shape (batch, heads, sequence, sequence)?This shape maps out every dimension of the parallel attention math:batch: Isolates independent sentences in the training pack.heads: Keeps the unique routing grid for each head completely separate.sequence (1st): Represents the source Query tokens (where we are looking from).sequence (2nd): Represents the target Key tokens (what we are looking at).A 4x4 slice inside a head shows exactly how much token i cares about token j.5. Why is \(W_{o}\) necessary after concatenation?When you concatenate the heads back together, they sit side-by-side as independent, isolated blocks of information. The final linear projection matrix (\(W_{o}\)) acts as a mixer. It allows the information discovered by Head 1, Head 2, and Head 4 to interact, blend, and map back into a cohesive, uniform d_model representation that downstream blocks can interpret.6. If one head learns nothing useful, does the whole attention layer fail?No. Multi-head attention is highly robust because the heads operate in parallel. If one head learns random noise or collapses, the remaining heads can easily compensate by carrying the useful relational signals. The downstream projection matrix (\(W_{o}\)) can also learn to down-weight or completely ignore the output coming from a broken head.7. Does having more heads always improve the model?No, there is a point of diminishing returns. If you increase heads too much, head_dim shrinks to a point where each head doesn't have enough dimensional capacity to capture complex structures. For instance, if d_model = 8 and you use 8 heads, each head only gets a head_dim = 1. A single scalar cannot hold enough expressive information to track meaningful relational concepts, hurting performance.