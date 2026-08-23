import os
import sys
import tempfile
import torch
import torch.nn as nn

# --- 1. Dynamic Path Resolution to Repository Root ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import the authentic core components built previously
from models.minigpt.config import MiniGPTConfig
from models.minigpt.model import MiniGPT
from data.minigpt.tokenizer import CharTokenizer
from data.minigpt.dataset import NextTokenDataset

def run_smoke_test():
    print("====================================================")
    print("         MINIGPT WEEK 2 SYSTEM SMOKE TEST           ")
    print("====================================================\n")
    
    torch.manual_seed(42)
    
    # Example validation text corpus
    smoke_text = (
        "the bank approved the loan.\n"
        "the bank reviewed the loan."
    )
    
    # ------------------------------------------------------------------
    # Milestone 1: Tokenizer can fit text
    # ------------------------------------------------------------------
    tokenizer = CharTokenizer(unk_token="?")
    tokenizer.fit(smoke_text)
    assert tokenizer.is_fitted, "Milestone 1 FAILED: Tokenizer not marked as fitted."
    print("✔ Milestone 1: Tokenizer successfully fitted the raw text.")
    
    # Encode complete stream for dataset tracking
    token_ids = tokenizer.encode(smoke_text)
    context_length = 8
    
    # ------------------------------------------------------------------
    # Milestone 2: Dataset produces input and target
    # ------------------------------------------------------------------
    dataset = NextTokenDataset(token_ids=token_ids, sequence_length=context_length)
    input_ids, target_ids = dataset[0]
    
    assert input_ids.shape == (context_length,), f"Unexpected input shape: {input_ids.shape}"
    assert target_ids.shape == (context_length,), f"Unexpected target shape: {target_ids.shape}"
    # Invariant check: Target is shifted right by exactly 1 position
    assert input_ids[1:].tolist() == target_ids[:-1].tolist(), "Dataset sequence shifting is misaligned!"
    print("✔ Milestone 2: NextTokenDataset safely splits inputs and shifted targets.")
    
    # Add fake batch dimension to tensors for standard model interface evaluation
    batch_input = input_ids.unsqueeze(0)   # shape: (1, context_length)
    batch_target = target_ids.unsqueeze(0) # shape: (1, context_length)
    
    # Initialize Configuration and Architecture Setup
    config = MiniGPTConfig(
        vocab_size=tokenizer.vocab_size,
        d_model=64,
        num_heads=2,
        d_ff=128,
        num_layers=1,
        max_sequence_length=16
    )
    model = MiniGPT(config)
    
    # ------------------------------------------------------------------
    # Milestone 3: Model produces logits
    # ------------------------------------------------------------------
    logits = model(batch_input)
    expected_shape = (1, context_length, config.vocab_size)
    assert logits.shape == expected_shape, f"Milestone 3 FAILED: Expected shape {expected_shape}, got {logits.shape}"
    print("✔ Milestone 3: MiniGPT forward graph processes shape to logits cleanly.")
    
    # ------------------------------------------------------------------
    # Milestone 4: Loss is finite
    # ------------------------------------------------------------------
    criterion = nn.CrossEntropyLoss()
    B, T, V = logits.shape
    loss = criterion(logits.reshape(B * T, V), batch_target.reshape(B * T))
    
    assert torch.isfinite(loss), f"Milestone 4 FAILED: Loss is not a finite scalar. Got: {loss.item()}"
    assert loss.item() > 0.0, "Loss evaluated to zero unexpectedly."
    print(f"✔ Milestone 4: Reshaped Cross-Entropy loss computed successfully (Value: {loss.item():.4f}).")
    
    # ------------------------------------------------------------------
    # Milestone 5: Backward pass works
    # ------------------------------------------------------------------
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    optimizer.zero_grad()
    
    # Verify starting baseline gradients are unallocated
    assert model.lm_head.weight.grad is None
    
    loss.backward()
    assert model.lm_head.weight.grad is not None, "Milestone 5 FAILED: No gradients present after backward call."
    assert torch.isfinite(model.lm_head.weight.grad).all(), "Encountered infinite/NaN values in the gradient registers."
    print("✔ Milestone 5: Backward pass executes cleanly without breaking the autograd graph.")
    
    # ------------------------------------------------------------------
    # Milestone 6: Optimizer updates at least one parameter
    # ------------------------------------------------------------------
    original_weights = model.lm_head.weight.clone().detach()
    optimizer.step()
    updated_weights = model.lm_head.weight.detach()
    
    # Assert parameters physically moved in memory away from original random configuration coordinates
    assert not torch.equal(original_weights, updated_weights), "Milestone 6 FAILED: Weights stayed identical after step call."
    print("✔ Milestone 6: Optimizer successfully shifts model parameters along gradients.")
    
    # ------------------------------------------------------------------
    # Milestone 7: Checkpoint saves
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp_dir:
        checkpoint_path = os.path.join(tmp_dir, "smoke_checkpoint.pt")
        
        save_dict = {
            "model_state_dict": model.state_dict(),
            "config": config,
            "vocabulary": tokenizer.char_to_id
        }
        torch.save(save_dict, checkpoint_path)
        assert os.path.exists(checkpoint_path), "Milestone 7 FAILED: Checkpoint file was not created on disk."
        print(f"✔ Milestone 7: State dictionaries successfully serialized to disk at temp path.")
        
        # ------------------------------------------------------------------
        # Milestone 8: Fresh model loads checkpoint
        # ------------------------------------------------------------------
        # STRICT RULE: Instantiating a completely fresh independent model object shell
        loaded_model = MiniGPT(config)
        
        # Verify it has different random initialized starting parameters from the trained model
        assert not torch.equal(loaded_model.lm_head.weight, model.lm_head.weight)
        
        # Inject saved checkpoint weights into the fresh instance
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        loaded_model.load_state_dict(checkpoint["model_state_dict"])
        loaded_model.eval()
        
        # Verify the fresh model parameters now match the trained parameters exactly
        assert torch.equal(loaded_model.lm_head.weight, model.lm_head.weight), "Milestone 8 FAILED: State mismatch."
        print("✔ Milestone 8: A separate fresh model instance successfully loads and maps saved parameter matrices.")
        
        # ------------------------------------------------------------------
        # Milestone 9: Loaded model produces valid output
        # ------------------------------------------------------------------
        with torch.no_grad():
            fresh_logits = loaded_model(batch_input)
            
        assert fresh_logits.shape == expected_shape, f"Milestone 9 FAILED: Invalid output shape {fresh_logits.shape}"
        assert torch.isfinite(fresh_logits).all(), "Loaded model inference execution returned non-finite scalars."
        print("✔ Milestone 9: Restored model successfully computes a valid, finite forward pass.")

    print("\n----------------------------------------------------")
    print("🎉 ALL 9 SMOKE TEST MILESTONES PASSED SUCCESSFULLY!")
    print("Your full pipeline path is structurally solid.")
    print("====================================================")

if __name__ == "__main__":
    run_smoke_test()
