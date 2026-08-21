import math
from pathlib import Path
import matplotlib.pyplot as plt
import torch


def softmax(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """Numerically stable softmax."""
    max_x, _ = torch.max(x, dim=dim, keepdim=True)
    exp_x = torch.exp(x - max_x)
    return exp_x / torch.sum(exp_x, dim=dim, keepdim=True)


def plot_attention_heatmap(
    weights: torch.Tensor, tokens: list[str], title: str, output_filename: str
):
    """Generates and saves a clean heatmap configuration for attention weights."""
    fig, ax = plt.subplots(figsize=(7, 6), dpi=150)

    # Plot the matrix using a clean sequential colormap
    cax = ax.matshow(weights.numpy(), cmap="Blues", vmin=0.0, vmax=1.0)
    fig.colorbar(cax, label="Attention Weight Value")

    # Set up accurate tick positioning
    ax.set_xticks(range(len(tokens)))
    ax.set_yticks(range(len(tokens)))

    # Apply token labels to structural axes
    ax.set_xticklabels(tokens, fontsize=11)
    ax.set_yticklabels(tokens, fontsize=11)

    # Shift tick positions to label row/col headers cleanly
    ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)

    # Labels and Layout Configuration
    ax.set_title(title, fontsize=13, weight="bold", pad=20)
    ax.set_xlabel("Keys (Tokens being attended to) ───>", labelpad=12, fontsize=11)
    ax.set_ylabel("Queries (Token looking for context) ───>", labelpad=12, fontsize=11)

    # Annotate cell numeric values text labels for easy human scannability
    for i in range(len(tokens)):
        for j in range(len(tokens)):
            val = weights[i, j].item()
            # Invert text color if background color gets dark for readability
            color = "white" if val > 0.5 else "black"
            ax.text(
                j, i, f"{val:.2f}", ha="center", va="center", color=color, weight="bold"
            )

    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches="tight")
    plt.close()
    print(f"🎨 Map exported successfully to: {output_filename}")


def run_visualization_pipeline():
    # 1. Setup Sample Dataset Inputs
    tokens = ["the", "bank", "approved", "loan"]
    seq_len = len(tokens)
    d_model = 16

    # Establish deterministic seeding
    torch.manual_seed(42)

    # 2. Simulate Input Representations and Random Projection Weights
    X = torch.randn(seq_len, d_model)
    W_Q = torch.randn(d_model, d_model)
    W_K = torch.randn(d_model, d_model)

    Q = X @ W_Q
    K = X @ W_K

    # 3. Calculate Base Scaled Attention Scores
    scores = (Q @ K.t()) / math.sqrt(d_model)

    # ----------------------------------------------------
    # Plot A: Standard Bidirectional Attention Matrix
    # ----------------------------------------------------
    weights_bidirectional = softmax(scores, dim=-1)
    plot_attention_heatmap(
        weights=weights_bidirectional,
        tokens=tokens,
        title="Standard Bidirectional Attention Weights\n(Random Initialized Weights)",
        output_filename="attention_matrix.png",
    )

    # ----------------------------------------------------
    # Plot B: Causal Masked Attention Matrix (Decoder/GPT style)
    # ----------------------------------------------------
    # Create lower-triangular binary matrix mask of shape (4, 4)
    # 1s on/below diagonal (keep), 0s above diagonal (mask future context)
    causal_mask = torch.tril(torch.ones(seq_len, seq_len))

    # Force future elements to large negative values so they vanish during softmax
    masked_scores = scores.masked_fill(causal_mask == 0, -1e9)
    weights_causal = softmax(masked_scores, dim=-1)

    plot_attention_heatmap(
        weights=weights_causal,
        tokens=tokens,
        title="Causal Autoregressive Attention Weights\n(Blocked Future Mask Context)",
        output_filename="causal_attention_matrix.png",
    )


if __name__ == "__main__":
    run_visualization_pipeline()
