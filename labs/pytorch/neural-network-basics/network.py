import torch
import torch.nn as nn

class SimpleNetwork(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.linear1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.linear1(x)
        x = self.relu(x)
        x = self.linear2(x)
        return x
    
class SequentialNetwork(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)
    
if __name__ == "__main__":
    IN_FEATURES = 10
    HIDDEN_FEATURES = 20
    OUT_FEATURES = 2

    model = SimpleNetwork(IN_FEATURES, HIDDEN_FEATURES, OUT_FEATURES)
    print("Model architecture: \n", model)

    dummy_input = torch.randn(4, IN_FEATURES)
    output = model(dummy_input)
    print("/nOutput Shape:", output.shape)

    model_sequence = SequentialNetwork(IN_FEATURES, HIDDEN_FEATURES, OUT_FEATURES)
    print("Sequential Model architecture: \n", model_sequence)