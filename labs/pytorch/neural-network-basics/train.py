import torch
import torch.nn as nn
import torch.optim as optim

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
    
IN_FEATURES = 5
HIDDEN_FEATURES = 10
OUT_FEATURES = 1
LEARNING_RATE = 0.1
EPOCHS = 1000

X_train = torch.randn(100, IN_FEATURES)
Y_train = X_train.sum(dim=1, keepdim=True) + torch.randn(100, 1) * 0.1

model = SimpleNetwork(IN_FEATURES, HIDDEN_FEATURES, OUT_FEATURES)
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=LEARNING_RATE)

print("Starting training...")

for epoch in range(EPOCHS):
    outputs = model(X_train)
    loss = criterion(outputs, Y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f'Epoch [{epoch + 1}/{EPOCHS}], Loss: {loss.item():.4f}')

print("Training complete.")