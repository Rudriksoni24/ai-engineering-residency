import math
import torch

def softmax(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    max_x, _ = torch.max(x, dim=dim, keepdim=True)
    exp_x = torch.exp(x - max_x)
    return exp_x / torch.sum(exp_x, dim=dim, keepdim=True)

def run_scaling_experiment():
    # Experimental Setup
    D_K_DIMENSIONS = [8, 64, 512]
    SEQUENCE_LENGTH = 4
    
    # Set seed for reproducible matrix statistics
    torch.manual_seed(42)

    print("=== STARTING ATTENTION SCALING EXPERIMENT ===")
    
    for d_k in D_K_DIMENSIONS:
        print(f"\n==========================================")
        print(f"🔬 Experiment Configuration: d_k = {d_k}")
        print(f"==========================================")
        
        # 1. Generate random Query and Key projections assuming N(0, 1) distribution
        Q = torch.randn(SEQUENCE_LENGTH, d_k)
        K = torch.randn(SEQUENCE_LENGTH, d_k)
        
        # ---------------------------------------------------------
        # Case A: Unscaled Attention Math (Raw Dot Products)
        # ---------------------------------------------------------
        scores_unscaled = torch.matmul(Q, K.t())
        probs_unscaled = softmax(scores_unscaled, dim=-1)
        
        # ---------------------------------------------------------
        # Case B: Scaled Attention Math (Divided by sqrt(d_k))
        # ---------------------------------------------------------
        scores_scaled = scores_unscaled / math.sqrt(d_k)
        probs_scaled = softmax(scores_scaled, dim=-1)
        
        # 2. Extract Metric Profiles
        print(f"{'Metric Profile':<25} | {'Unscaled (Raw)':<20} | {'Scaled (1/sqrt(d_k))':<20}")
        print("-" * 73)
        
        # Score Ranges
        unscaled_range_str = f"[{scores_unscaled.min():.2f}, {scores_unscaled.max():.2f}]"
        scaled_range_str = f"[{scores_scaled.min():.2f}, {scores_scaled.max():.2f}]"
        print(f"{'1. Score Range [Min, Max]':<25} | {unscaled_range_str:<20} | {scaled_range_str:<20}")
        
        # Maximum Probabilities
        print(f"{'2. Max Peak Probability':<25} | {probs_unscaled.max():.4f}@{probs_unscaled.argmax().item():<14} | {probs_scaled.max():.4f}@{probs_scaled.argmax().item():<14}")
        
        # Distribution Sharpness (Average Peak Confidence Per Row)
        row_max_unscaled_mean = probs_unscaled.max(dim=-1)[0].mean().item()
        row_max_scaled_mean = probs_scaled.max(dim=-1)[0].mean().item()
        print(f"{'3. Avg Row Peak Sharpness':<25} | {row_max_unscaled_mean:.4f} (Highly Peaked) | {row_max_scaled_mean:.4f} (Uniform/Smooth)")

if __name__ == "__main__":
    run_scaling_experiment()
