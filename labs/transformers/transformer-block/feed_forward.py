import torch
import torch.nn as nn

class FeedForwardNetwork(nn.Module):
    def __init__(self, d_model: int = 512, d_ff: int = 2048):
        """
        Position-wise Feed-Forward Network as defined in the Transformer paper.
        FFN(x) = max(0, xW1 + b1)W2 + b2
        """
        super().__init__()
        
        # 1. First linear projection expands dimension from d_model to d_ff
        self.w_1 = nn.Linear(d_model, d_ff)
        
        # 2. Activation function (ReLU)
        self.relu = nn.ReLU()
        
        # 3. Second linear projection contracts dimension back from d_ff to d_model
        self.w_2 = nn.Linear(d_ff, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for the FFN block.
        Input shape:  (batch_size, seq_len, d_model)
        Output shape: (batch_size, seq_len, d_model)
        """
        # Linear (d_model -> d_ff) -> ReLU -> Linear (d_ff -> d_model)
        return self.w_2(self.relu(self.w_1(x)))


# --- Local Verification Script ---
if __name__ == "__main__":
    torch.manual_seed(42)
    
    # 1. Setup mock parameters based on the challenge configuration
    batch_size = 2
    seq_len = 10
    d_model = 512
    d_ff = 2048
    
    # 2. Create the network and mock input tensor
    ffn = FeedForwardNetwork(d_model=d_model, d_ff=d_ff)
    mock_input = torch.randn(batch_size, seq_len, d_model)
    
    # 3. Run a forward pass
    output = ffn(mock_input)
    
    print("--- Feed-Forward Network Verification ---")
    print(f"Input Shape:  {list(mock_input.shape)} (Expected: [2, 10, 512])")
    print(f"Output Shape: {list(output.shape)} (Expected: [2, 10, 512])")
    
    # 4. Check that gradients flow correctly through both internal layers
    loss = output.sum()
    loss.backward()
    
    w1_grad = ffn.w_1.weight.grad is not None and torch.isfinite(ffn.w_1.weight.grad).all()
    w2_grad = ffn.w_2.weight.grad is not None and torch.isfinite(ffn.w_2.weight.grad).all()
    
    print(f"w_1 layer gradients active and finite: {w1_grad}")
    print(f"w_2 layer gradients active and finite: {w2_grad}")
