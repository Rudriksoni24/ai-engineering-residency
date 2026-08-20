import torch
import matplotlib.pyplot as plt

def positional_encoding(sequence_length: int, d_model: int) -> torch.Tensor:
    """
    Computes a deterministic sinusoidal positional encoding matrix.
    
    Formula:
        PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
        PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
        
    Args:
        sequence_length (int): Total number of tokens in the sequence (max_len).
        d_model (int): Hidden dimension size of the embedding model features.
        
    Returns:
        torch.Tensor: A 2D matrix of shape (sequence_length, d_model)
    """
    # 1. Initialize an empty tensor placeholder
    pe = torch.zeros(sequence_length, d_model)
    
    # 2. Generate the positions vector: shape (sequence_length, 1)
    position = torch.arange(0, sequence_length, dtype=torch.float).unsqueeze(1)
    
    # 3. Compute the exponential scaling factor for the denominators: shape (d_model // 2,)
    # We step by 2 to group the identical frequencies for both even (sine) and odd (cosine) dims
    div_term = torch.exp(torch.arange(0, d_model, 2, dtype=torch.float) * -(torch.log(torch.tensor(10000.0)) / d_model))
    
    # 4. Apply Sine to even feature dimensions (0, 2, 4, ...)
    pe[:, 0::2] = torch.sin(position * div_term)
    
    # 5. Apply Cosine to odd feature dimensions (1, 3, 5, ...)
    pe[:, 1::2] = torch.cos(position * div_term)
    
    return pe

# --- Quick Verification and Visual Inspection ---
if __name__ == "__main__":
    # Test with custom, dynamic dimensions to prove zero hardcoding
    SEQ_LEN = 50
    D_MODEL = 128
    
    pe_matrix = positional_encoding(sequence_length=SEQ_LEN, d_model=D_MODEL)
    
    # 1. Shape Assertion Check
    print(f"📦 Generated PE Shape: {pe_matrix.shape}")
    assert pe_matrix.shape == (SEQ_LEN, D_MODEL), f"Shape error! Got {pe_matrix.shape}"
    print("✅ Shape validation successful!")
    
    # 2. Value Determinism Check
    second_run = positional_encoding(sequence_length=SEQ_LEN, d_model=D_MODEL)
    assert torch.equal(pe_matrix, second_run), "Error: Matrix output must be 100% deterministic."
    print("✅ Determinism validation successful!")

    # 3. Mathematical Alignment Check (Even vs Odd properties)
    print(f"✨ Feature 0 (Even - Sin) at Pos 0: {pe_matrix[0, 0].item():.4f}") # sin(0) = 0
    print(f"✨ Feature 1 (Odd - Cos)  at Pos 0: {pe_matrix[0, 1].item():.4f}") # cos(0) = 1
    
    # 4. Optional: Export a visual heatmap chart to inspect progression waves
    plt.figure(figsize=(10, 6), dpi=150)
    plt.pcolormesh(pe_matrix.numpy(), cmap='RdBu')
    plt.xlabel('Embedding Dimension (d_model)')
    plt.ylabel('Token Position (sequence_length)')
    plt.colorbar(label='Encoding Intensity Value')
    plt.title(f'Sinusoidal Positional Encoding Matrix ({SEQ_LEN}x{D_MODEL})', weight='bold')
    
    output_filename = "positional-encoding-space.png"
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close()
    print(f"\n🎨 Diagnostic wavefront map successfully saved as: {output_filename}")
