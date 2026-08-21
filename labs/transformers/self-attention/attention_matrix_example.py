import math
import torch

def softmax(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """Numerically stable softmax."""
    max_x, _ = torch.max(x, dim=dim, keepdim=True)
    exp_x = torch.exp(x - max_x)
    return exp_x / torch.sum(exp_x, dim=dim, keepdim=True)

def run_attention_matrix_example():
    # 1. Define sentence tokens and structural dimensions
    tokens = ["the", "bank", "approved", "loan"]
    SEQUENCE_LENGTH = len(tokens)
    D_MODEL = 8  # Keep dimensions small for easy visual tracking
    
    # Establish deterministic initialization for reproducibility
    torch.manual_seed(101)
    
    # 2. Represent each token with an input feature matrix
    # Shape: (4, 8) -> (sequence_length, d_model)
    X = torch.randn(SEQUENCE_LENGTH, D_MODEL)
    
    # 3. Simulate Linear Projection Matrices for Q, K, and V
    # In a real model, these weights are learned during training.
    # Here they are random parameters initializing the routing architecture.
    W_Q = torch.randn(D_MODEL, D_MODEL)
    W_K = torch.randn(D_MODEL, D_MODEL)
    W_V = torch.randn(D_MODEL, D_MODEL)
    
    # Compute Query, Key, and Value states via matrix multiplication
    Q = X @ W_Q  # Shape: (4, 8)
    K = X @ W_K  # Shape: (4, 8)
    V = X @ W_V  # Shape: (4, 8)
    
    # 4. Compute Scaled Attention Scores
    # Q @ K.T maps shape (4, 8) @ (8, 4) -> (4, 4) attention score matrix
    d_k = K.size(-1)
    raw_scores = Q @ K.t()
    scaled_scores = raw_scores / math.sqrt(d_k)
    
    # 5. Extract Attention Weights via Softmax
    attention_weights = softmax(scaled_scores, dim=-1)
    
    # 6. Format and Display the Scaled Attention Matrix
    print("=== DYNAMIC TRANSFORMER ATTENTION WEIGHTS MATRIX ===")
    print("⚠️  Note: Vectors are initialized randomly. This displays routing mechanics, NOT language understanding.")
    print("-" * 72)
    
    # Print Column Header Row
    header_row = f"{'':<12}" + "".join([f"{token:<14}" for token in tokens])
    print(header_row)
    print("-" * 72)
    
    # Print Rows (Queries) looking at Columns (Keys)
    for i, query_token in enumerate(tokens):
        row_str = f"{query_token:<12}"
        for j in range(SEQUENCE_LENGTH):
            weight = attention_weights[i, j].item()
            row_str += f"{weight:<14.4f}"
        print(row_str)
        
    print("-" * 72)
    
    # 7. Verification of Row Distribution
    print(f"📊 Softmax Row Distribution Verification (Sum across dim=-1):")
    for i, token in enumerate(tokens):
        print(f"  • Row '{token:<8}' Sum: {attention_weights[i].sum().item():.4f}")

if __name__ == "__main__":
    run_attention_matrix_example()
