import torch
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Setup the text details and inputs
tokens = ["the", "bank", "approved", "loan"]
seq_len = len(tokens)
batch_size = 1
num_heads = 2
d_model = 8

# For reproducible, clear visualizations across runs
torch.manual_seed(42)

# 2. Instantiate and generate random attention weights 
# (Simulating the output matrix of your forward pass setup)
q = torch.randn(batch_size, seq_len, d_model)
k = torch.randn(batch_size, seq_len, d_model)

# Re-use your scaled dot product math from Task 6
head_dim = d_model // num_heads
# Simulate split-head shape (batch, heads, seq, head_dim)
q_split = q.view(batch_size, seq_len, num_heads, head_dim).transpose(1, 2)
k_split = k.view(batch_size, seq_len, num_heads, head_dim).transpose(1, 2)

# Raw dot product scores: (1, 2, 4, 4)
scores = torch.matmul(q_split, k_split.transpose(-2, -1)) / (head_dim ** 0.5)

# Apply the causal mask
causal_mask = torch.tril(torch.ones(seq_len, seq_len))
masked_scores = scores.masked_fill(causal_mask == 0, -1e9)
attention_weights = torch.softmax(masked_scores, dim=-1)

# Extract tensor to CPU/NumPy for plotting -> shape: (2, 4, 4)
attn_matrix = attention_weights[0].detach().cpu().numpy()

# 3. Plotting Loop to save files
for h in range(num_heads):
    plt.figure(figsize=(6, 5))
    
    # Generate the heatmap visualization
    sns.heatmap(
        attn_matrix[h], 
        xticklabels=tokens, 
        yticklabels=tokens, 
        annot=True,       # Shows raw percentage numbers inside blocks
        fmt=".3f",        # Decimal format
        cmap="Blues",     # Blue color gradient 
        vmin=0, vmax=1,   # Fixed bounds for comparative scales
        cbar=True
    )
    
    plt.title(f"Head {h + 1} Attention Pattern (Causal)")
    plt.xlabel("Key Tokens (Attended To)")
    plt.ylabel("Query Tokens (Looking From)")
    plt.tight_layout()
    
    # Save target filenames
    filename = f"head_{h + 1}_attention.png"
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Successfully generated and saved: {filename}")

    import torch

# Constants
batch_size = 1
seq_len = 4
d_model = 8
configs = [1, 2, 4]  # Different num_heads configurations

# Fixed input representation for "the bank approved loan"
torch.manual_seed(42)
q = torch.randn(batch_size, seq_len, d_model)
k = torch.randn(batch_size, seq_len, d_model)
causal_mask = torch.tril(torch.ones(seq_len, seq_len))

print("--- Multi-Head Attention Configuration Experiment ---")
for num_heads in configs:
    head_dim = d_model // num_heads
    
    # Simulate head splitting
    q_split = q.view(batch_size, seq_len, num_heads, head_dim).transpose(1, 2)
    k_split = k.view(batch_size, seq_len, num_heads, head_dim).transpose(1, 2)
    
    # Compute attention scores matrix
    scores = torch.matmul(q_split, k_split.transpose(-2, -1)) / (head_dim ** 0.5)
    masked_scores = scores.masked_fill(causal_mask == 0, -1e9)
    attention_matrix = torch.softmax(masked_scores, dim=-1)
    
    # Simulate head merging back to original structural state
    output_shape = (batch_size, seq_len, d_model)
    
    print(f"\n[Configuration: num_heads = {num_heads}]")
    print(f" -> Head Dimension (d_model // num_heads) : {head_dim}")
    print(f" -> Attention Matrix Shape                : {list(attention_matrix.shape)}")
    print(f" -> Number of Individual Attention Maps  : {attention_matrix.shape[1]}")
    print(f" -> Final Output Shape (Merged)          : {output_shape}")

