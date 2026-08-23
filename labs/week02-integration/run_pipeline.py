import os
import sys
import time
import random
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader

# --- 1. Deterministic Engineering Seed Configurations ---
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# Enforce strict deterministic internal algorithm execution layout for PyTorch backends
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# --- 2. Dynamic Path Resolution to Repository Root ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import the official custom components built previously
from models.minigpt.config import MiniGPTConfig
from models.minigpt.model import MiniGPT
from data.minigpt.tokenizer import CharTokenizer
from data.minigpt.dataset import NextTokenDataset


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    
    print("====================================================")
    print("      MINIGPT DETERMINISTIC INTEGRATION PIPELINE    ")
    print(f"      Active Seed Configuration Lock: {SEED}        ")
    print("====================================================\n")
    
    # 1. Load Training Text
    training_text = (
        "machine learning is fun.\n"
        "machine learning is powerful.\n"
        "machine learning requires data."
    )
    print("Step 1: Loaded training text corpus.")
    
    # 2. Fit Tokenizer
    tokenizer = CharTokenizer(unk_token="?")
    tokenizer.fit(training_text)
    vocab_size = tokenizer.vocab_size
    print(f"Step 2: Fitted character tokenizer. Vocab Size: {vocab_size} unique tokens.")
    
    # 3. Encode Text
    token_ids = tokenizer.encode(training_text)
    print(f"Step 3: Encoded text stream into {len(token_ids)} token integer IDs.")
    
    # 4. Create Dataset
    context_length = 16
    dataset = NextTokenDataset(token_ids=token_ids, sequence_length=context_length)
    print(f"Step 4: Created NextTokenDataset chunks. Total accessible slices: {len(dataset)}.")
    
    # 5. Create DataLoader (Disable shuffle to ensure perfect sequence order tracking)
    batch_size = 4
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    print("Step 5: Wrapped dataset in Deterministic PyTorch DataLoader.")
    
    # 6. Create MiniGPTConfig
    config = MiniGPTConfig(
        vocab_size=vocab_size,
        d_model=128,
        num_heads=4,
        d_ff=256,
        num_layers=2,
        max_sequence_length=32
    )
    print("Step 6: Initialised Model Configuration.")
    
    # 7. Create MiniGPT Model
    model = MiniGPT(config).to(device)
    for block in model.blocks:
        block.dropout.p = 0.0
    print(f"Step 7: Initialised MiniGPT architecture on target device: `{device}`.")
    
    # 8. Train
    print("\nStep 8: Commencing optimization micro-training loops...")
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4)
    model.train()
    
    num_epochs = 80
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        batch_count = 0
        for input_ids, target_ids in dataloader:
            input_ids, target_ids = input_ids.to(device), target_ids.to(device)
            
            optimizer.zero_grad()
            logits = model(input_ids)
            
            B, T, V = logits.shape
            loss = criterion(logits.reshape(B * T, V), target_ids.reshape(B * T))
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            batch_count += 1
            
        if (epoch + 1) % 20 == 0 or epoch == 0:
            avg_loss = epoch_loss / batch_count
            print(f"   -> Epoch [{epoch+1:2d}/{num_epochs}] | Training Loss: {avg_loss:.4f}")
            
    # 9. Save Checkpoint
    checkpoint_dir = os.path.join(root_dir, "checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)
    integration_checkpoint = os.path.join(checkpoint_dir, "integration_minigpt.pt")
    
    torch.save({
        "model_state_dict": model.state_dict(),
        "config": config,
        "vocabulary": tokenizer.char_to_id
    }, integration_checkpoint)
    print(f"\nStep 9: Learned parameter states serialized to disk at: {integration_checkpoint}")
    
    # 10. Create Fresh Model
    fresh_model = MiniGPT(config).to(device)
    print("Step 10: Instantiated a completely fresh, un-trained model copy.")
    
    # 11. Load Checkpoint
    checkpoint = torch.load(integration_checkpoint, map_location=device, weights_only=False)
    fresh_model.load_state_dict(checkpoint["model_state_dict"])
    fresh_model.eval()
    print("Step 11: Injected saved checkpoint state weights back into fresh model weights.")
    
    # 12. Generate Text
    print("\nStep 12: Launching autoregressive text generation check...")
    prompt = "machine learning requires "
    print(f"   -> Input Prompt String : '{prompt}'")
    
    current_tokens = torch.tensor([tokenizer.encode(prompt)], dtype=torch.long, device=device)
    max_new_tokens = 6
    
    with torch.no_grad():
        for _ in range(max_new_tokens):
            if current_tokens.size(1) > context_length:
                input_tokens = current_tokens[:, -context_length:]
            else:
                input_tokens = current_tokens
                
            logits = fresh_model(input_tokens)
            next_token_logits = logits[:, -1, :]
            next_token_id = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            current_tokens = torch.cat((current_tokens, next_token_id), dim=1)
            
    generated_output = tokenizer.decode(current_tokens[0].tolist())
    print(f"   -> Full Predicted Sequence : '{generated_output}'")
    print("\n----------------------------------------------------")
    print("🎉 REPRODUCIBLE PIPELINE COMPLETED SUCCESSFULLY!")
    print("====================================================")

if __name__ == "__main__":
    main()
