import torch
from positional_encoding import positional_encoding

def run_experiment():
    # 1. Setup Experiment Dimensions
    # Using 3 tokens for "bank", "transfer", "approved"
    SEQUENCE_LENGTH = 3  
    D_MODEL = 64  # Configurable embedding dimension hidden size

    print("=== Starting Position-Aware Embedding Experiment ===")
    
    # 2. Step 1: Generate Token Embeddings (Simulated for this lab using random values)
    # Shape: (3, 64)
    token_embeddings = torch.randn(SEQUENCE_LENGTH, D_MODEL)
    
    # 3. Step 2: Generate Deterministic Positional Encoding
    # Shape: (3, 64)
    pos_encoding = positional_encoding(sequence_length=SEQUENCE_LENGTH, d_model=D_MODEL)
    
    # 4. Step 3: Combine them element-wise (Token + Position)
    # Shape remains: (3, 64)
    position_aware_embeddings = token_embeddings + pos_encoding

    # 5. Print Required Structural Shape Formats
    print(f"Input embedding shape:     {token_embeddings.shape}")
    print(f"Positional encoding shape: {pos_encoding.shape}")
    print(f"Final embedding shape:     {position_aware_embeddings.shape}\n")

    # 6. Print First Few Values for Direct Comparison (Token 0 vs Token 1 for first 4 features)
    print("=== First 4 Feature Values for Detailed Comparison ===")
    print("-" * 75)
    print(f"{'Component':<25} | {'Token 0 (bank)':<22} | {'Token 1 (transfer)':<22}")
    print("-" * 75)
    
    # Extract string formatted representations of the first 4 indices
    tok_0_vals = [f"{x:.4f}" for x in token_embeddings[0, :4].tolist()]
    tok_1_vals = [f"{x:.4f}" for x in token_embeddings[1, :4].tolist()]
    
    pe_0_vals  = [f"{x:.4f}" for x in pos_encoding[0, :4].tolist()]
    pe_1_vals  = [f"{x:.4f}" for x in pos_encoding[1, :4].tolist()]
    
    final_0_vals = [f"{x:.4f}" for x in position_aware_embeddings[0, :4].tolist()]
    final_1_vals = [f"{x:.4f}" for x in position_aware_embeddings[1, :4].tolist()]

    print(f"{'1. Token Embeddings':<25} | {str(tok_0_vals):<22} | {str(tok_1_vals):<22}")
    print(f"{'2. Positional Encoding':<25} | {str(pe_0_vals):<22} | {str(pe_1_vals):<22}")
    print(f"{'3. Final Position-Aware':<25} | {str(final_0_vals):<22} | {str(final_1_vals):<22}")
    print("-" * 75)

    # Conceptual confirmation note on token index 0
    # At position 0, even indices are sin(0)=0 and odd indices are cos(0)=1
    print("\n💡 Note: Look closely at '2. Positional Encoding' for Token 0.")
    print(f"   Even index 0 is {pe_0_vals[0]} (sin), while odd index 1 is {pe_0_vals[1]} (cos).")
    print("   This confirms positional context is perfectly injected without warping structure.")

if __name__ == "__main__":
    run_experiment()
