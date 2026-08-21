import math
import torch
import torch.nn as nn


class MultiHeadAttention(nn.Module):

    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        # 1. Validate that the hidden dimension can be divided evenly by the number of heads
        if d_model % num_heads != 0:
            raise ValueError(
                f"d_model ({d_model}) must be divisible by num_heads ({num_heads})"
            )

        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        # 2. Create separate learnable linear projection matrices using nn.Linear
        self.Wq = nn.Linear(d_model, d_model, bias=False)
        self.Wk = nn.Linear(d_model, d_model, bias=False)
        self.Wv = nn.Linear(d_model, d_model, bias=False)
        self.Wo = nn.Linear(d_model, d_model, bias=False)

    def _stable_softmax(self, x: torch.Tensor, dim: int = -1) -> torch.Tensor:
        """Numerically stable softmax implemented over a specified tensor dimension."""
        max_x, _ = torch.max(x, dim=dim, keepdim=True)
        exp_x = torch.exp(x - max_x)
        return exp_x / torch.sum(exp_x, dim=dim, keepdim=True)

    def forward(
        self, x: torch.Tensor, mask: torch.Tensor = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for Multi-Head Attention.

        Args:
            x (torch.Tensor): Input representation of shape (batch_size,
              seq_len, d_model)
            mask (torch.Tensor, optional): Mask tensor where 1 means keep, 0
              means mask out. Shape must be broadcastable to (batch_size,
              num_heads, seq_len, seq_len)

        Returns:
            tuple[torch.Tensor, torch.Tensor]: (output_tensor, attention_weights)
        """
        batch_size, seq_len, _ = x.shape

        # 3. Project input tensor X into Q, K, and V spaces
        # Shapes: (batch_size, seq_len, d_model)
        Q = self.Wq(x)
        K = self.Wk(x)
        V = self.Wv(x)

        # 4. Split into multiple heads and transpose to align for parallel computation
        # Reshape: (B, T, D) -> (B, T, H, d_k)
        # Transpose: (B, T, H, d_k) -> (B, H, T, d_k)
        Q = Q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(
            1, 2
        )
        K = K.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(
            1, 2
        )
        V = V.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(
            1, 2
        )

        # 5. Perform Scaled Dot-Product Attention parallelised across all heads
        # Raw Scores: (B, H, T, d_k) @ (B, H, d_k, T) -> (B, H, T, T)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(
            self.head_dim
        )

        # Apply mask before softmax if present
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # Compute stable attention distributions
        weights = self._stable_softmax(scores, dim=-1)

        # Compute output per head: (B, H, T, T) @ (B, H, T, d_k) -> (B, H, T, d_k)
        attention_out = torch.matmul(weights, V)

        # 6. Concatenate heads back into a single cohesive matrix
        # Transpose back: (B, H, T, d_k) -> (B, T, H, d_k)
        # .contiguous() forces sequential memory management before a view flattening
        # Flatten Shape: (B, T, H * d_k) -> (B, T, D)
        concat_out = (
            attention_out.transpose(1, 2)
            .contiguous()
            .view(batch_size, seq_len, self.d_model)
        )

        # 7. Apply the final linear output projection Wo
        output = self.Wo(concat_out)

        return output, weights

    def split_heads(self,x):
        """
        Splits the d_model dimension into (num_heads, head_dim) and permutes.
        Input shape:  (batch, seq_len, d_model)
        Output shape: (batch, num_heads, seq_len, head_dim)
        """
        batch_size, seq_len, d_model = x.size()
        
        # Calculate individual head dimension (8 / 2 = 4 in your example)
        assert d_model % self.num_heads == 0, "d_model must be divisible by num_heads"
        # head_dim = d_model // self.num_heads
        
        # 1. Reshape: (batch, seq_len, num_heads, head_dim)
        x = x.view(batch_size, seq_len, self.num_heads, self.head_dim)
        
        # 2. Permute: (batch, num_heads, seq_len, head_dim)
        x = x.transpose(1, 2) 
        
        return x

    def merge_heads(self,x):
        """
        Reverses the split_heads operation.
        Input shape:  (batch, num_heads, seq_len, head_dim)
        Output shape: (batch, seq_len, d_model)
        """
        batch_size, num_heads, seq_len, head_dim = x.size()
        
        # 1. Permute back: (batch, seq_len, num_heads, head_dim)
        # .contiguous() ensures memory layout is linear before reshaping
        x = x.transpose(1, 2).contiguous()
        
        # 2. Reshape back: (batch, seq_len, num_heads * head_dim)
        d_model = num_heads * head_dim
        x = x.view(batch_size, seq_len, d_model)
        
        return x

    def compute_per_head_attention(self, Q, K, V, mask=None):
        """
        Executes Scaled Dot-Product Attention independently across num_heads.
        
        Inputs:
            Q: (batch_size, num_heads, seq_len, head_dim)
            K: (batch_size, num_heads, seq_len, head_dim)
            V: (batch_size, num_heads, seq_len, head_dim)
        """
        # 1. Extract head_dim from the final structural parameter column
        head_dim = K.size(-1)
        
        # 2. Compute Q @ K.T independently for each head channel
        # K.transpose(-2, -1) flips the last two dimensions to shape: (batch_size, num_heads, head_dim, seq_len)
        # Resulting score shape: (batch_size, num_heads, seq_len, seq_len)
        raw_scores = torch.matmul(Q, K.transpose(-2, -1))
        
        # 3. Divide by the square root of the head dimension to protect gradient flow stability
        scaled_scores = raw_scores / math.sqrt(head_dim)
        
        # 4. Inject causal masking parameters if configured
        if mask is not None:
            # mask is broadcasted across the head dimension channel automatically
            scaled_scores = scaled_scores.masked_fill(mask == 0, -1e9)
            
        # 5. Execute stable softmax over the final token look axis (dim=-1)
        # The distributions sum up to 1.0 along the row dimension inside every individual head
        max_scores, _ = torch.max(scaled_scores, dim=-1, keepdim=True)
        exp_scores = torch.exp(scaled_scores - max_scores)
        attention_weights = exp_scores / torch.sum(exp_scores, dim=-1, keepdim=True)
        
        # 6. Extract final Context representations by multiplying weights with Values
        # Matrix calculation maps: (B, H, T, T) @ (B, H, T, d_k) -> (B, H, T, d_k)
        per_head_outputs = torch.matmul(attention_weights, V)
        
        return per_head_outputs, attention_weights

    def forward1(self, q, k, v, mask=None):
            # 1. Split heads to get shape: (batch, heads, seq_len, head_dim)
            q = self.split_heads(q)
            k = self.split_heads(k)
            v = self.split_heads(v)
            
            # 2. Compute raw attention scores -> shape: (batch, heads, seq_len, seq_len)
            head_dim = q.size(-1)
            scores = torch.matmul(q, k.transpose(-2, -1)) / torch.sqrt(torch.tensor(head_dim, dtype=torch.float32))
            
            # 3. Apply Causal Mask if requested
            if mask is not None:
                # mask shape is (seq_len, seq_len)
                # scores shape is (batch, heads, seq_len, seq_len)
                # Broadcasting automatically expands mask to match scores
                scores = scores.masked_fill(mask == 0, -1e9)
                
            # 4. Compute attention weights
            attention_weights = torch.softmax(scores, dim=-1)
            
            # 5. Weighted sum of values -> shape: (batch, heads, seq_len, head_dim)
            out = torch.matmul(attention_weights, v)
            
            # 6. Merge heads back -> shape: (batch, seq_len, d_model)
            return self.merge_heads(out), attention_weights


# --- Quick Shape Validation Run ---
if __name__ == "__main__":
    # # Test Parameters matching Task 1 guidelines exactly
    B, T, D, H = 1, 4, 8, 2

    # # Instantiate block
    mha = MultiHeadAttention(d_model=D, num_heads=H)

    # # Initialize a mock token sequence tensor
    # mock_input = torch.randn(B, T, D)
    # print(f"📥 Mandated Input Shape (X):           {mock_input.shape}")

    # # Process forward pass
    # out, attn_weights = mha(mock_input)

    # print(f"📦 Attention Routing Weights Matrix:    {attn_weights.shape}")
    # print(f"📤 Final Concatenated Output Shape:      {out.shape}")

    # # Confirm matrix dimensions matching
    # assert out.shape == (B, T, D), "Output spatial shape tracing broken!"
    # assert attn_weights.shape == (
    #     B,
    #     H,
    #     T,
    #     T,
    # ), "Attention tracking weight matrix shape broken!"
    # print("\n✅ Multi-Head Attention shape validations complete and correct!")

    # 1. Initialize tensor with your target shapes: (batch=1, seq_len=4, d_model=8)
    x = torch.randn(1, 4, 8)
    num_heads = 2
    # 2. Run Forward Split
    split_x = mha.split_heads(x)
    print("Forward Transformation:")
    print(f"Original shape: {x.shape} -> Split shape: {split_x.shape}") 
    # Expected: torch.Size([1, 2, 4, 4])
    # 3. Run Reverse Merge
    merged_x = mha.merge_heads(split_x)
    print("\nReverse Transformation:")
    print(f"Split shape: {split_x.shape} -> Merged shape: {merged_x.shape}") 
    # Expected: torch.Size([1, 4, 8])
     
    # 4. Check that data integrity is identical
    print(f"\nAre tensors perfectly identical? {torch.equal(x, merged_x)}")

    # --- Hyperparameters Setup ---
    BATCH_SIZE = 1
    SEQ_LEN = 4
    D_MODEL = 8
    NUM_HEADS = 2
    HEAD_DIM = D_MODEL // NUM_HEADS  # 8 // 2 = 4

    # Initialize a mock multi-head output representation 
    # Shape: (batch_size, num_heads, sequence_length, head_dim) -> (1, 2, 4, 4)
    torch.manual_seed(42)
    attention_out = torch.randn(BATCH_SIZE, NUM_HEADS, SEQ_LEN, HEAD_DIM)

    print("=== Starting Output Projection Pipeline ===")
    print(f"📥 Input Per-Head Shape:              {attention_out.shape}")

    # 1. Step 1: Revert structural axis positions back to original timeline
    # (B, H, T, d_k) -> (B, T, H, d_k)
    transposed_out = attention_out.transpose(1, 2)

    # 2. Step 2: Flatten the last two dimensions (Concatenation)
    # .contiguous() forces memory rows to re-align sequentially before flattening
    # Shape transforms: (1, 4, 2, 4) -> (1, 4, 8)
    concat_out = transposed_out.contiguous().view(BATCH_SIZE, SEQ_LEN, D_MODEL)
    print(f"🧩 After Concatenation Shape:          {concat_out.shape}")

    # 3. Step 3: Apply the Linear Output Projection Matrix (W_o)
    # W_o maps from d_model (8) back to d_model (8) to allow residual stream additions
    Wo = nn.Linear(D_MODEL, D_MODEL, bias=False)
    final_output = Wo(concat_out)

    print(f"📤 Final Layer Output Shape:           {final_output.shape}")

    # 4. Mandatory Shape Assertion Check
    assert final_output.shape == (BATCH_SIZE, SEQ_LEN, D_MODEL), "Output shape tracing failed!"
    print("\n✅ Verification successful! Output dimensions align perfectly to (1, 4, 8).")

    q = torch.randn(BATCH_SIZE, SEQ_LEN, D_MODEL)
    k = torch.randn(BATCH_SIZE, SEQ_LEN, D_MODEL)
    v = torch.randn(BATCH_SIZE, SEQ_LEN, D_MODEL)

    # Create the 2D causal mask -> shape: (4, 4)
    causal_mask = torch.tril(torch.ones(SEQ_LEN, SEQ_LEN))
    
    # Run forward pass with mask applied
    _, attn_weights = mha.forward1(q, k, v, mask=causal_mask)
    
    print(f"Attention Weights Shape: {attn_weights.shape}")
    # Expected: torch.Size([1, 2, 4, 4])

    # Check each head individually to prove future_token_attention ≈ 0
    for h in range(NUM_HEADS):
        print(f"\n--- Checking Head {h} ---")
        head_weights = attn_weights[0, h]
        print(torch.round(head_weights, decimals=4))
        
        # Pull out the upper triangular values above the diagonal
        upper_tri_elements = torch.triu(head_weights, diagonal=1)
        
        # Assert that all future attention elements are virtually 0
        is_masked_correctly = torch.allclose(upper_tri_elements, torch.zeros_like(upper_tri_elements), atol=1e-6)
        print(f"Are all future token attentions zero? {is_masked_correctly}")