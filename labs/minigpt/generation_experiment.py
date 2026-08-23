import os
import sys

# 1. Resolve paths to find the root directory containing 'models'
# This climbs up from labs/minigpt/tests_training.py -> labs/minigpt/ -> labs/ -> root repository folder
current_dir = os.path.dirname(os.path.abspath(__file__))      # labs/minigpt
parent_dir = os.path.dirname(current_dir)                    # labs
root_dir = os.path.dirname(parent_dir)                        # main root repository folder

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Ensure the script can also locate relative modules inside its local folder
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Now perform your cross-folder imports safely
import torch
from models.minigpt.config import MiniGPTConfig
from models.minigpt.model import MiniGPT
from data.minigpt.tokenizer import CharTokenizer 

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

def run_greedy_generation(model, tokenizer, prompt, max_new_tokens=30, context_length=16):
    model.eval()
    encoded = tokenizer.encode(prompt)
    current_tokens = torch.tensor([encoded], dtype=torch.long)
    
    with torch.no_grad():
        for _ in range(max_new_tokens):
            if current_tokens.size(1) > context_length:
                input_tokens = current_tokens[:, -context_length:]
            else:
                input_tokens = current_tokens
                
            logits = model(input_tokens)
            next_token_logits = logits[:, -1, :]
            next_token_id = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            current_tokens = torch.cat((current_tokens, next_token_id), dim=1)
            
    return tokenizer.decode(current_tokens.tolist()[0])

def main():
    torch.manual_seed(42)
    
    # 1. Reconstruct baseline configurations and tokenizer matching your training run
    raw_text = (
        "machine learning is fun.\n"
        "machine learning is powerful.\n"
        "machine learning requires data."
    )
    tokenizer = CharTokenizer()
    tokenizer.fit(raw_text)
    
    config = MiniGPTConfig(
        vocab_size=tokenizer.vocab_size,
        d_model=128,
        num_heads=4,
        d_ff=256,
        num_layers=2,
        max_sequence_length=32
    )
    
    prompt = "machine"
    
    print("====================================================")
    print("   MINIGPT BEFORE VS AFTER TRAINING EXPERIMENT      ")
    print("====================================================\n")
    
    # --- PHASE 1: GENERATION BEFORE TRAINING ---
    # Model initialized with random weights
    untrained_model = MiniGPT(config)
    before_output = run_greedy_generation(untrained_model, tokenizer, prompt)
    print(f"--- 1. Before Training ---")
    print(f"Prompt : '{prompt}'")
    print(f"Output : '{before_output}'\n")
    
    # --- PHASE 2: GENERATION AFTER TRAINING ---
    # Load optimized parameters from disk
    checkpoint_path = os.path.join(root_dir, "checkpoints", "minigpt.pt")
    if not os.path.exists(checkpoint_path):
        print(f"❌ Error: Run train_minigpt.py first to create a checkpoint.")
        return
        
    trained_model = MiniGPT(config)
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    trained_model.load_state_dict(checkpoint["model_state_dict"])
    
    after_output = run_greedy_generation(trained_model, tokenizer, prompt)
    print(f"--- 2. After Training ---")
    print(f"Prompt : '{prompt}'")
    print(f"Output : '{after_output}'\n")

if __name__ == "__main__":
    main()
 