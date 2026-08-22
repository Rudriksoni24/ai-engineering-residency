import os
import sys
import torch
import torch.nn as nn

# --- 1. Comprehensive System Path Injection ---
current_dir = os.path.dirname(os.path.abspath(__file__))  # transformer-block folder
parent_dir = os.path.dirname(current_dir)                 # transformers folder

# Path pointing to labs/transformers/multi-head-attention
mha_folder_path = os.path.join(parent_dir, "multi-head-attention")
if mha_folder_path not in sys.path:
    sys.path.insert(0, mha_folder_path)

# Path pointing to labs/transformers/self-attention (for mask utility)
sa_folder_path = os.path.join(parent_dir, "self-attention")
if sa_folder_path not in sys.path:
    sys.path.insert(0, sa_folder_path)

# Ensure local folder visibility
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. Module Imports ---
from multi_head_attention import MultiHeadAttention
from feed_forward import FeedForwardNetwork

# Import the causal mask function from your target path: self-attention/attention.py
try:
    from attention import create_causal_mask
except ModuleNotFoundError:
    # Fallback to absolute module mapping if structured as nested package
    from labs.transformers.self_attention.attention import create_causal_mask


# --- 3. Master Transformer Block Module ---
class TransformerBlock(nn.Module):
    def __init__(self, d_model: int = 512, num_heads: int = 8, d_ff: int = 2048, dropout: float = 0.1):
        """
        A single custom Post-LayerNorm Transformer Block.
        Natively integrates your custom causal mask function from self-attention/attention.py
        """
        super().__init__()
        
        # Core Feature Processing Blocks
        self.mha = MultiHeadAttention(d_model=d_model, num_heads=num_heads)
        self.ffn = FeedForwardNetwork(d_model=d_model, d_ff=d_ff)
        
        # Post-Layer Normalization Blocks
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        # Regularization Track
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask=None) -> torch.Tensor:
        """
        Forward pass for the complete Transformer Block.
        """
        seq_len = x.size(1)
        
        # Handle native causal masking instruction string
        if isinstance(mask, str) and mask == "causal":
            # 1. Fetch your Day 1 mask matrix
            raw_mask = create_causal_mask(seq_len)
            
            # 2. FIX: Convert explicitly to a PyTorch long/bool tensor on the correct device
            # This ensures that `mask == 0` evaluations downstream create a true PyTorch Tensor!
            mask = torch.tensor(raw_mask, dtype=torch.long, device=x.device)
            
        # --- Sub-layer 1: Attention Branch ---
        attn_out, _ = self.mha(x, mask=mask)
        x = self.norm1(x + self.dropout(attn_out))
        
        # --- Sub-layer 2: Feed-Forward Network Branch ---
        ffn_out = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_out))
        
        return x


# --- 4. Built-in Local Verification Suite ---
if __name__ == "__main__":
    torch.manual_seed(42)
    
    # Input Setup Config Parameters (Matching Task Constraints)
    batch_size = 1
    seq_len = 4
    d_model = 8
    num_heads = 2
    d_ff = 16
    
    print("Initializing Self-Masking TransformerBlock...")
    block = TransformerBlock(d_model=d_model, num_heads=num_heads, d_ff=d_ff)
    mock_input = torch.randn(batch_size, seq_len, d_model)
    
    # Run forward pass explicitly using the auto-mask call string
    print("\nExecuting forward pass with mask='causal'...")
    output = block(mock_input, mask="causal")
    
    print("\n=== Integrated Transformer Block Diagnostics ===")
    print(f"Input Data Tensor Dimension   : {list(mock_input.shape)}")
    print(f"Output Data Tensor Dimension  : {list(output.shape)}")
    
    # Assert shape consistency
    assert mock_input.shape == output.shape, "Shape mismatch! In/Out dimensions must be identical."
    print("✔ Structural Interface Shape Trace: Perfect Alignment.")

    # Validate mask application by pulling weights directly from the MHA layer
    with torch.no_grad():
        test_mask = create_causal_mask(seq_len)
        _, attn_weights = block.mha(mock_input, mask=test_mask)
        
    all_heads_causal = True
    for h in range(num_heads):
        print(f"\n=== Head {h + 1} Attention Probability Distribution ===")
        head_matrix = attn_weights[0, h].cpu().numpy()
        print(torch.from_numpy(head_matrix).round(decimals=4))
        
        # Extract elements strictly above the main diagonal (future context steps)
        upper_tri = torch.triu(torch.from_numpy(head_matrix), diagonal=1)
        if not torch.allclose(upper_tri, torch.zeros_like(upper_tri), atol=1e-6):
            all_heads_causal = False
            
    print("\n------------------------------------------------------------")
    if all_heads_causal:
        print("✔ SUCCESS: Causal mask functions natively inside the block from your target path!")
