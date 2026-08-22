import os
import sys
import torch

# 1. Path resolution to ensure root directory visibility for cross-folder imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # labs folder
root_dir = os.path.dirname(parent_dir)      # root repository folder

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.minigpt.config import MiniGPTConfig
from models.minigpt.model import MiniGPT

def main():
    torch.manual_seed(42)
    
    # 2. Configuration Parameters Setup
    config = MiniGPTConfig(
        vocab_size=1000,
        d_model=128,
        num_heads=4,
        d_ff=512,
        num_layers=4,
        max_sequence_length=64,
    )
    
    # 3. Model Initialization
    model = MiniGPT(config)
    
    # 4. Generate Random Input Token IDs
    input_ids = torch.randint(
        0,
        config.vocab_size,
        (2, 10)
    )
    
    # 5. Forward Execution Pass
    logits = model(input_ids)
    
    # 6. Parameter Counting Logic
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # 7. Formatted Terminal Reports
    print("=== MiniGPT Execution Diagnostic Trace ===")
    print(f"Input IDs shape     : {list(input_ids.shape)}")
    print(f"Logits shape        : {list(logits.shape)}")
    print("\n--- Dimensional Validation ---")
    print(f"Input IDs:\n {tuple(input_ids.shape)}")
    print(f"Logits:\n {tuple(logits.shape)}")
    print("\n--- Model Parameter Tracking ---")
    print(f"Total Parameters    : {total_params:,}")
    print(f"Trainable Parameters: {trainable_params:,}")

if __name__ == "__main__":
    main()
