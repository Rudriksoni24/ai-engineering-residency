import os
import sys
import torch

# Ensure parent path tracking handles cross-folder imports cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from transformer_block import TransformerBlock

def test_gradient_flow():
    # Setup test dimensions
    batch_size = 2
    sequence_length = 10
    d_model = 512
    num_heads = 8
    d_ff = 2048
    
    torch.manual_seed(42)
    
    # 1. Instantiate the integrated Block
    model = TransformerBlock(d_model=d_model, num_heads=num_heads, d_ff=d_ff)
    
    # 2. Track input nodes explicitly 
    x = torch.randn(batch_size, sequence_length, d_model, requires_grad=True)
    
    # 3. Compute Forward Path Sequence
    output = model(x, mask="causal")
    
    # 4. Generate Backprop Graph Objective
    loss = output.mean()
    loss.backward()
    
    # 5. Build Parameter Map Checklist based on your exact variable names
    # This captures your MHA projections, FFN layers, and LayerNorm weight/bias vectors
    parameter_targets = {
        "Q Projection (MHA)": getattr(model.mha, "Wq", None),
        "K Projection (MHA)": getattr(model.mha, "Wk", None),
        "V Projection (MHA)": getattr(model.mha, "Wv", None),
        "Output Projection (MHA)": getattr(model.mha, "Wo", None),
        "FFN First Layer (W1)": getattr(model.ffn, "w_1", None),
        "FFN Second Layer (W2)": getattr(model.ffn, "w_2", None),
        "LayerNorm 1 (Attention Block)": model.norm1,
        "LayerNorm 2 (FFN Block)": model.norm2,
    }
    
    print("=== Transformer Block Gradient Flow Verification ===")
    print(f"Graph Loss Objective Value: {loss.item():.6f}\n")
    
    all_passed = True
    
    for label, layer in parameter_targets.items():
        if layer is None:
            print(f"❌ {label}: Layer object could not be extracted.")
            all_passed = False
            continue
            
        # Check weight gradient (or general layer parameter matrix gradients)
        has_grad = False
        finite_grad = False
        
        if hasattr(layer, 'weight') and layer.weight is not None:
            has_grad = layer.weight.grad is not None
            if has_grad:
                finite_grad = torch.isfinite(layer.weight.grad).all().item()
        
        # Output confirmation status to console
        if has_grad and finite_grad:
            print(f"✔ {label:<30} -> Gradient Verified (Status: Active & Finite)")
        else:
            print(f"❌ {label:<30} -> Gradient FAILED (Grad present: {has_grad}, Finite: {finite_grad})")
            all_passed = False
            
    # Check Input Tensors as well
    input_grad = x.grad is not None and torch.isfinite(x.grad).all().item()
    print(f"\n✔ Input Tensor X Shortcut Pathway  -> Gradient Verified: {input_grad}")
    
    print("\n---------------------------------------------------")
    if all_passed and input_grad:
        print("🎉 SUCCESS: Every single sub-layer layer parameter can actively participate in training!")
    else:
        print("⚠️ FAILURE: Broken chain detected in the autograd path. Check your tensor detach/operations.")

if __name__ == "__main__":
    test_gradient_flow()
