import os
import sys
import tempfile
import pytest
import torch
import torch.nn as nn

# --- 1. Dynamic Path Resolution ---
current_dir = os.path.dirname(os.path.abspath(__file__))      # labs/minigpt
parent_dir = os.path.dirname(current_dir)                    # labs
root_dir = os.path.dirname(parent_dir)                        # main repository folder

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- 2. Safe Component Imports ---
from models.minigpt.config import MiniGPTConfig
from models.minigpt.model import MiniGPT
from data.minigpt.tokenizer import CharTokenizer
from data.minigpt.dataset import NextTokenDataset


class TestMiniGPTTrainingPipeline:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        torch.manual_seed(42)
        self.text_corpus = "machine learning is fun.\nmachine learning is powerful.\nmachine learning requires data."
        self.seq_len = 8
        self.d_model = 64
        
        # Initialize Tokenizer and Fit
        self.tokenizer = CharTokenizer()
        self.tokenizer.fit(self.text_corpus)
        
        # Initialize Model Configurations
        self.config = MiniGPTConfig(
            vocab_size=self.tokenizer.vocab_size,
            d_model=self.d_model,
            num_heads=2,
            d_ff=128,
            num_layers=1,
            max_sequence_length=32
        )
        self.model = MiniGPT(self.config)
        self.token_ids = self.tokenizer.encode(self.text_corpus)
        self.dataset = NextTokenDataset(self.token_ids, sequence_length=self.seq_len)

    # --- Tokenizer Sub-Suite Verification ---
    def test_01_tokenizer_fit_works(self):
        """[x] Tokenizer fit works."""
        fresh_tokenizer = CharTokenizer()
        assert not fresh_tokenizer.is_fitted
        fresh_tokenizer.fit("abc")
        assert fresh_tokenizer.is_fitted
        assert fresh_tokenizer.vocab_size > 0

    def test_02_encode_works(self):
        """[x] Encode works."""
        encoded = self.tokenizer.encode("machine")
        assert isinstance(encoded, list)
        assert len(encoded) == 7
        assert all(isinstance(i, int) for i in encoded)

    def test_03_decode_works(self):
        """[x] Decode works."""
        sample_ids = [self.tokenizer.char_to_id[c] for c in "fun"]
        decoded = self.tokenizer.decode(sample_ids)
        assert isinstance(decoded, str)
        assert decoded == "fun"

    def test_04_encode_decode_round_trip_works(self):
        """[x] Encode/decode round trip works."""
        original_text = "learning"
        encoded = self.tokenizer.encode(original_text)
        decoded = self.tokenizer.decode(encoded)
        assert original_text == decoded

    # --- Dataset Sub-Suite Verification ---
    def test_05_dataset_input_shape_is_correct(self):
        """[x] Dataset input shape is correct."""
        input_ids, _ = self.dataset[0]
        assert input_ids.shape == (self.seq_len,)
        assert input_ids.dtype == torch.long

    def test_06_dataset_target_shape_is_correct(self):
        """[x] Dataset target shape is correct."""
        _, target_ids = self.dataset[0]
        assert target_ids.shape == (self.seq_len,)
        assert target_ids.dtype == torch.long

    def test_07_target_is_shifted_by_one_token(self):
        """[x] Target is shifted by one token."""
        input_ids, target_ids = self.dataset[0]
        # Invariant: input_ids[1:] must match target_ids[:-1] exactly
        assert input_ids[1:].tolist() == target_ids[:-1].tolist()
        assert target_ids[-1].item() == self.token_ids[self.seq_len]

    # --- Model & Training Optimization Verification ---
    def test_08_model_forward_pass_works(self):
        """[x] Model forward pass works."""
        input_ids, _ = self.dataset[0]
        # Simulate a batch of 1
        batch_input = input_ids.unsqueeze(0)
        logits = self.model(batch_input)
        assert logits.shape == (1, self.seq_len, self.config.vocab_size)

    def test_09_loss_can_calculated(self):
        """[x] Loss can be calculated."""
        input_ids, target_ids = self.dataset[0]
        batch_input = input_ids.unsqueeze(0)
        batch_target = target_ids.unsqueeze(0)
        
        logits = self.model(batch_input)
        B, T, V = logits.shape
        
        criterion = nn.CrossEntropyLoss()
        loss = criterion(logits.reshape(B * T, V), batch_target.reshape(B * T))
        assert loss.item() > 0.0

    def test_10_backward_pass_produces_gradients(self):
        """[x] Backward pass produces gradients."""
        input_ids, target_ids = self.dataset[0]
        batch_input = input_ids.unsqueeze(0)
        batch_target = target_ids.unsqueeze(0)
        
        logits = self.model(batch_input)
        B, T, V = logits.shape
        criterion = nn.CrossEntropyLoss()
        loss = criterion(logits.reshape(B * T, V), batch_target.reshape(B * T))
        
        # Confirm empty baseline tracking states
        assert self.model.lm_head.weight.grad is None
        
        loss.backward()
        assert self.model.lm_head.weight.grad is not None
        assert torch.isfinite(self.model.lm_head.weight.grad).all()

    def test_11_optimizer_changes_parameters(self):
        """[x] Optimizer changes parameters."""
        input_ids, target_ids = self.dataset[0]
        batch_input = input_ids.unsqueeze(0)
        batch_target = target_ids.unsqueeze(0)
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-2)
        
        # Clone original structural weight state matrix before optimization step
        original_weights = self.model.lm_head.weight.clone().detach()
        
        logits = self.model(batch_input)
        B, T, V = logits.shape
        criterion = nn.CrossEntropyLoss()
        loss = criterion(logits.reshape(B * T, V), batch_target.reshape(B * T))
        
        loss.backward()
        optimizer.step()
        
        updated_weights = self.model.lm_head.weight.detach()
        # Verify the underlying parameter floats physically moved away from original baseline coordinates
        assert not torch.equal(original_weights, updated_weights)

    # --- Serialization & Checkpoint Lifecycle Verification ---
    def test_12_checkpoint_saves_and_13_loads(self):
        """
        [x] Checkpoint saves.
        [x] Checkpoint loads.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = os.path.join(tmpdir, "test_minigpt.pt")
            
            # Pack payload state structure
            save_payload = {
                "model_state_dict": self.model.state_dict(),
                "config": self.config,
                "vocabulary": self.tokenizer.char_to_id
            }
            
            # 12. Save Checkpoint Verification
            torch.save(save_payload, checkpoint_path)
            assert os.path.exists(checkpoint_path)
            
            # 13. Load Checkpoint Verification
            loaded_payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
            assert "model_state_dict" in loaded_payload
            assert "config" in loaded_payload
            assert "vocabulary" in loaded_payload
            
            # Verify data payload configuration parameters survived serialization intact
            assert loaded_payload["config"].d_model == self.d_model
            assert loaded_payload["vocabulary"] == self.tokenizer.char_to_id
