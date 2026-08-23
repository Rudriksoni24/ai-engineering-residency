import os
import sys
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# --- 1. Repository Path Configuration ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.minigpt.config import MiniGPTConfig
from models.minigpt.model import MiniGPT
from data.minigpt.tokenizer import CharTokenizer
from data.minigpt.dataset import NextTokenDataset

def run_tracked_training():
    # Select execution hardware device
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    torch.manual_seed(42)
    
    # Target Overfitting Text Dataset Configuration
    raw_text = (
        "machine learning is fun.\n"
        "machine learning is powerful.\n"
        "machine learning requires data."
    )
    
    # Fit Character Tokenizer
    tokenizer = CharTokenizer()
    tokenizer.fit(raw_text)
    vocab_size = tokenizer.vocab_size
    token_ids = tokenizer.encode(raw_text)
    
    # Pipeline Parameters
    context_length = 16
    batch_size = 4
    num_epochs = 100
    
    config = MiniGPTConfig(
        vocab_size=vocab_size,
        d_model=128,
        num_heads=4,
        d_ff=256,
        num_layers=2,
        max_sequence_length=32
    )
    
    # Initialize model and shift to device
    model = MiniGPT(config).to(device)
    
    # Disable dropout for strict memorization verification
    for block in model.blocks:
        block.dropout.p = 0.0
        
    dataset = NextTokenDataset(token_ids=token_ids, sequence_length=context_length)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4)
    num_parameters = sum(p.numel() for p in model.parameters())
    
    print("====================================================")
    print("      MINIGPT METRIC TRACKED RUN STARTING           ")
    print("====================================================\n")
    
    model.train()
    start_time = time.time()
    initial_loss = None
    final_loss = None
    
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        batch_count = 0
        
        for input_ids, target_ids in dataloader:
            input_ids = input_ids.to(device)
            target_ids = target_ids.to(device)
            
            optimizer.zero_grad()
            logits = model(input_ids)
            
            B, T, V = logits.shape
            logits_flat = logits.reshape(B * T, V)
            targets_flat = target_ids.reshape(B * T)
            
            loss = criterion(logits_flat, targets_flat)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            batch_count += 1
            
        avg_loss = epoch_loss / batch_count
        if epoch == 0:
            initial_loss = avg_loss
        if epoch == num_epochs - 1:
            final_loss = avg_loss
            
        print(f"Epoch: {epoch + 1}")
        print(f"Loss: {avg_loss:.4f}\n")
        
    training_time = time.time() - start_time
    
    # --- 2. Serialize and Save Checkpoint Payload ---
    checkpoint_dir = os.path.join(root_dir, "checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(checkpoint_dir, "minigpt.pt")
    
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": config,
            "vocabulary": tokenizer.char_to_id,  # Serialise exact mapping
        },
        checkpoint_path,
    )
    print(f"✔ Checkpoint successfully serialized to: {checkpoint_path}")

    # --- 3. Programmatically Generate Documentation ---
    doc_path = os.path.join(checkpoint_dir, "metadata.md")
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write("# MiniGPT Checkpoint Metadata\n\n")
        f.write("## Model Configuration\n")
        f.write(f"- **d_model**: {config.d_model}\n")
        f.write(f"- **num_heads**: {config.num_heads}\n")
        f.write(f"- **d_ff**: {config.d_ff}\n")
        f.write(f"- **num_layers**: {config.num_layers}\n")
        f.write(f"- **max_sequence_length**: {config.max_sequence_length}\n\n")
        
        f.write("## Vocabulary Properties\n")
        f.write(f"- **Total Vocabulary Size**: {vocab_size} unique characters\n")
        f.write(f"- **Character Lookup Directory Map**: `{tokenizer.char_to_id}`\n\n")
        
        f.write("## Training Performance Metadata\n")
        f.write(f"- **Initial Starting Loss**: {initial_loss:.4f}\n")
        f.write(f"- **Final Optimized Convergence Loss**: {final_loss:.4f}\n")
        f.write(f"- **Total Architectural Learnable Parameters**: {num_parameters:,}\n")
        f.write(f"- **Total Core Optimization Runtime**: {training_time:.2f} seconds\n")
        f.write(f"- **Target Acceleration Compute Device**: `{device}`\n")
        f.write(f"- **Dataset Size**: {len(raw_text)} raw characters\n")
        
    print(f"✔ Metadata documentation written to: {doc_path}")

if __name__ == "__main__":
    run_tracked_training()
