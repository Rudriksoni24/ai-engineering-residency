import torch
import torch.nn as nn

# 1. Setup mock dims (matching your current model scale)
batch_size = 2
seq_len = 3
d_model = 8  # Simplified for clean printing

torch.manual_seed(42)
x = torch.randn(batch_size, seq_len, d_model) * 10 + 5  # Scaled to emphasize norm shifts

# 2. Instantiate PyTorch LayerNorm over the feature dimension
layer_norm = nn.LayerNorm(d_model)

# Disable learnable parameters adjustments for raw numerical tracking
with torch.no_grad():
    x_norm = layer_norm(x)

# 3. Analyze a single specific token (e.g., Batch 0, Token 1)
sample_before = x[0, 1]
sample_after = x_norm[0, 1]

print("=== LayerNorm Dimensional Experiment ===")
print(f"Original Token Features:\n {sample_before}")
print(f"Normalized Token Features:\n {sample_after}\n")

print("--- Statistical Tracking (Across d_model dimension) ---")
print(f"Before Norm -> Mean: {sample_before.mean().item():.6f} | Variance: {sample_before.var(unbiased=False).item():.6f}")
print(f"After Norm  -> Mean: {sample_after.mean().item():.6f} | Variance: {sample_after.var(unbiased=False).item():.6f}")
