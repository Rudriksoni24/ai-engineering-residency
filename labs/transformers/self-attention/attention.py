import torch
import math

def softmax(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """
    Computes the numerically stable softmax over a specified dimension.
    
    Formula:
        softmax(x) = exp(x - max(x)) / sum(exp(x - max(x)))
    """
    # Find the maximum value along the specified dimension for subtraction stability
    # keepdim=True preserves dimensions for correct matrix broadcasting alignment
    max_x, _ = torch.max(x, dim=dim, keepdim=True)
    
    # Subtract max and compute exponential
    exp_x = torch.exp(x - max_x)
    
    # Divide by the element-wise sum along the same dimension
    return exp_x / torch.sum(exp_x, dim=dim, keepdim=True)

def scaled_dot_product_attention(
    Q: torch.Tensor, 
    K: torch.Tensor, 
    V: torch.Tensor, 
    mask: torch.Tensor = None
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Computes Scaled Dot-Product Attention.
    
    Args:
        Q (torch.Tensor): Query matrix of shape (..., seq_len, d_k)
        K (torch.Tensor): Key matrix of shape (..., seq_len, d_k)
        V (torch.Tensor): Value matrix of shape (..., seq_len, d_v)
        mask (torch.Tensor, optional): Mask tensor of shape broadcastable to attention scores.
                                      Should contain 1 (or True) for elements to keep, 
                                      and 0 (or False) for elements to mask out.
                                      
    Returns:
        tuple[torch.Tensor, torch.Tensor]: (output context matrix, attention weights matrix)
    """
    # 1. Get the dimension size of the keys (d_k) from the last axis
    d_k = K.size(-1)
    
    # 2. Compute raw attention scores by multiplying Queries and Keys
    # We transpose the last two dimensions of K (.transpose(-2, -1)) to support batched inputs
    scores = torch.matmul(Q, K.transpose(-2, -1))
    
    # 3. Scale scores by the square root of d_k to prevent gradient vanishing issues
    scores = scores / math.sqrt(d_k)
    
    # 4. Apply mask if provided
    # Masked positions are filled with an extremely large negative number (-1e9)
    # This forces their softmax value to become exactly 0.0
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
        
    # 5. Calculate attention weights using your stable softmax implementation
    weights = softmax(scores, dim=-1)
    
    # 6. Compute final output vector representations by multiplying weights with Values
    output = torch.matmul(weights, V)
    
    return output, weights

def create_causal_mask(sequence_length):
    """
    Creates a causal mask of shape (sequence_length, sequence_length).
    Positions with 1 (or True) are kept, while future positions (0 or False) 
    will be filled with a large negative value before softmax.
    """
    # 1. Create a matrix of ones
    ones = torch.ones(sequence_length, sequence_length)
    
    # 2. Keep only the lower triangular part (including the diagonal)
    mask = torch.tril(ones)
    
    return mask


# --- Verification Routine ---
if __name__ == "__main__":
    # 1. Configure properties matching constraints
    SEQUENCE_LENGTH = 4
    D_MODEL = 8  # For this simple setup, d_k = d_v = d_model = 8
    
    # 2. Initialize dummy matrices with unique sequences to easily trace indices
    torch.manual_seed(42)  # For deterministic outputs
    Q = torch.randn(SEQUENCE_LENGTH, D_MODEL)
    K = torch.randn(SEQUENCE_LENGTH, D_MODEL)
    V = torch.randn(SEQUENCE_LENGTH, D_MODEL)
    
    print("=== Step 1: Input Matrix Structural Properties ===")
    print(f"Query Matrix (Q) shape: {Q.shape}  | (sequence_length, d_model)")
    print(f"Key Matrix (K) shape:   {K.shape}  | (sequence_length, d_model)")
    print(f"Value Matrix (V) shape: {V.shape}  | (sequence_length, d_model)\n")
    
    # 3. Calculate attention weights and output
    output, weights = scaled_dot_product_attention(Q, K, V)
    
    print("=== Step 2: Attention Computation Outputs ===")
    print(f"Attention Weights shape: {weights.shape} | Expected: ({SEQUENCE_LENGTH}, {SEQUENCE_LENGTH})")
    print(f"Final Output shape:      {output.shape}  | Expected: ({SEQUENCE_LENGTH}, {D_MODEL})")
    
    # 4. Enforce structural assertions
    assert weights.shape == (SEQUENCE_LENGTH, SEQUENCE_LENGTH), "Attention weights dimension error!"
    assert output.shape == (SEQUENCE_LENGTH, D_MODEL), "Output context dimensions error!"
    print("\n✅ Verification successful! Tensor dimension shapes align perfectly.")

    # 5. Core Architectural Interpretation Trace
    print("\n=== Step 3: Structural Interrogation & Interpretation ===")
    print("Row/Column mapping inside our Attention Matrix weights:")
    print("-" * 65)
    print(f"Row Index (Query)   | Column Index (Key)    | Attention Weight")
    print("-" * 65)
    
    # Print a trace snippet showing how token 0 asks for data across all tokens
    for col_idx in range(SEQUENCE_LENGTH):
        weight_val = weights[0, col_idx].item()
        print(f"Token 0 (Querying)  | Token {col_idx} (Attended To) | Weight: {weight_val:.4f}")
    print("-" * 65)
    print("💡 Confirmation: Softmax sums up across rows. Row total =", weights[0].sum().item())


    # Example Usage:
    seq_len = 4
    mask = create_causal_mask(seq_len)

    # Applying the mask to attention scores before softmax
    attention_scores = torch.randn(seq_len, seq_len)
    large_negative_value = -1e9

    # Replace 0s with -inf / large negative value
    masked_attention = attention_scores.masked_fill(mask == 0, large_negative_value)
    print("\n=== Step 4: Causal Mask Application ===")
    print("Original Attention Scores:\n", attention_scores)
    print("\nCausal Mask:\n", mask)
    print("\nMasked Attention Scores (Future Context Blocked):\n", masked_attention)

    # Setup fixed sequence length and random scores for demonstration
    seq_len = 4
    torch.manual_seed(42)  # For reproducible scores

    # 1. Simulate raw attention scores (Q @ K.T)
    scores = torch.randn(seq_len, seq_len)

    # 2. Generate the causal mask
    mask = torch.tril(torch.ones(seq_len, seq_len))

    # 3. Apply Softmax to Run 1: Unmasked Attention
    unmasked_attention = torch.softmax(scores, dim=-1)

    # 4. Apply Mask and Softmax to Run 2: Causal Attention
    # Replace upper triangle zeros with -1e9 before softmax
    masked_scores = scores.masked_fill(mask == 0, -1e9)
    causal_attention = torch.softmax(masked_scores, dim=-1)

    print("--- Run 1: Unmasked Attention Weights ---")
    print(torch.round(unmasked_attention, decimals=4))

    print("\n--- Run 2: Causal Masked Attention Weights ---")
    print(torch.round(causal_attention, decimals=4))