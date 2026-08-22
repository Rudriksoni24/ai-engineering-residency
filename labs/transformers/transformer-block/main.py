import os
import sys
import torch

# 1. Ensure path resolution matches your folder layout configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import your finalized TransformerBlock
from transformer_block import TransformerBlock

def main():
    # Fixed execution parameters from task constraints
    batch_size = 2
    sequence_length = 10
    d_model = 512
    num_heads = 8
    d_ff = 2048
    
    torch.manual_seed(42)
    
    # 2. Instantiate the custom scratch-built Transformer Block
    block = TransformerBlock(
        d_model=d_model, 
        num_heads=num_heads, 
        d_ff=d_ff, 
        dropout=0.1
    )
    
    # 3. Generate random input representation matching target dimensions
    x = torch.randn(batch_size, sequence_length, d_model)
    
    # 4. Step-by-step pipeline tracing using your sub-blocks
    # This shows exactly what is happening inside the forward pass
    # 3. Shape Tracing
    with torch.no_grad():
        # FIX: Generate the actual PyTorch tensor mask for inner block testing
        # Import 'create_causal_mask' at the top of main.py if you haven't already!
        from transformer_block import create_causal_mask
        actual_tensor_mask = create_causal_mask(sequence_length)
        
        # Pass the tensor matrix to the inner MHA layer instead of the string "causal"
        attn_out, _ = block.mha(x, mask=actual_tensor_mask)
        
        # B. Pull out intermediate FFN shape before compression (W1 step)
        ffn_intermediate = block.ffn.w_1(x) 
        
        # C. Pull out final FFN output shape from your code's FFN component
        ffn_out = block.ffn(x)
        
        # D. Execute your entire TransformerBlock pass (this supports the "causal" string natively!)
        final_output = block(x, mask="causal")

    # 5. Formal formatted output logging
    print("=== Transformer Block Dimensional Shape Tracing ===")
    print(f"Input shape          : {list(x.shape)}")
    print(f"Attention output shape: {list(attn_out.shape)}")
    print(f"FFN intermediate shape: {list(ffn_intermediate.shape)}")
    print(f"FFN output shape     : {list(ffn_out.shape)}")
    print(f"Final output shape   : {list(final_output.shape)}")
    print("\n---------------------------------------------------")
    print(f"Input:  {tuple(x.shape)}")
    print(f"Output: {tuple(final_output.shape)}")

if __name__ == "__main__":
    main()
