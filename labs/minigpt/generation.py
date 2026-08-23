import os
import sys
import torch

# 1. Resolve paths to find the root directory containing 'models'
# This climbs up from labs/minigpt/generation.py -> labs/minigpt/ -> labs/ -> root repository folder
current_dir = os.path.dirname(os.path.abspath(__file__))      # labs/minigpt
parent_dir = os.path.dirname(current_dir)                    # labs
root_dir = os.path.dirname(parent_dir)                        # main root repository folder

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Ensure the script can also locate relative modules inside its local folder
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Now perform your cross-folder imports safely
from models.minigpt.model import MiniGPT
from data.minigpt.tokenizer import CharTokenizer

def run_generation():
    # 2. Select execution hardware device matching availability
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    
    # 3. Path resolution to locate the trained checkpoint file
    checkpoint_path = os.path.join(root_dir, "checkpoints", "minigpt.pt")
    if not os.path.exists(checkpoint_path):
        print(f"❌ ERROR: Checkpoint file not found at: {checkpoint_path}")
        print("Please run 'train_minigpt.py' first to generate the checkpoint payload.")
        return

    # FIX: Register your custom configuration class as a safe type for unpickling
    from models.minigpt.config import MiniGPTConfig
    torch.serialization.add_safe_globals([MiniGPTConfig])

    print("Loading optimized checkpoint state payload from disk...")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Extract structural configuration blocks and vocabulary rules
    config = checkpoint["config"]
    vocab_map = checkpoint["vocabulary"]
    
    # 4. Reconstruct and configure Tokenizer structure from saved metadata
    tokenizer = CharTokenizer()
    tokenizer.char_to_id = vocab_map
    tokenizer.id_to_char = {v: k for k, v in vocab_map.items()}
    tokenizer.chars = sorted(vocab_map.keys())
    tokenizer.is_fitted = True
    
    # 5. Initialize model architecture and inject learned parameters
    model = MiniGPT(config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()  # Set to evaluation mode to disable dropout tracks
    
    # --- 6. The Autoregressive Generation Core Pipeline ---
    prompt = "machine learning "
    max_new_tokens = 30
    
    print(f"\nPrompt: '{prompt}'")
    
    # Step A: Tokenizer converts prompt string to token IDs
    encoded_prompt = tokenizer.encode(prompt)
    
    # Step B: Convert to PyTorch tensor format and add batch dimension -> shape: (1, seq_len)
    current_tokens = torch.tensor([encoded_prompt], dtype=torch.long, device=device)
    
    generated_ids = []
    
    print("Generating remaining text autoregressively...", end="", flush=True)
        # Set this explicitly to match your exact training setup block limits
    context_length = 16 

    with torch.no_grad():
        for _ in range(max_new_tokens):
            # FIX: Crop the input tokens strictly to the context length used in training (16)
            # If current_tokens has shape (1, 18), it crops to the most recent 16 characters
            if current_tokens.size(1) > context_length:
                input_tokens = current_tokens[:, -context_length:]
            else:
                input_tokens = current_tokens
                
            # MiniGPT forward pass execution
            logits = model(input_tokens)
            
            # Pull strictly from the last sequence index position [-1]
            next_token_logits = logits[:, -1, :]
            
            # Select next token ID using greedy argmax selection
            next_token_id = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            
            # Append token ID onto the growing track matrix
            current_tokens = torch.cat((current_tokens, next_token_id), dim=1)
            
            # Collect and print token instantly
            new_id = next_token_id.item()
            generated_ids.append(new_id)
            print(tokenizer.decode([new_id]), end="", flush=True)
            
    print("\n\n====================================================")
    print("             GENERATION ROUTINE RESULTS             ")
    print("====================================================")
    full_sequence_ids = current_tokens[0].tolist()
    print(f"Complete Full Generated Output:\n'{tokenizer.decode(full_sequence_ids)}'")
    print("====================================================")

if __name__ == "__main__":
    run_generation()
