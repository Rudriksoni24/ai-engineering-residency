import os
import sys
import pytest
import torch

# Resolve paths to find the root directory containing 'models' and sister 'labs' folders
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # labs folder
root_dir = os.path.dirname(parent_dir)      # root repository folder

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.minigpt.config import MiniGPTConfig
from models.minigpt.model import MiniGPT

class TestMiniGPTCompleteSuite:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        torch.manual_seed(42)
        self.vocab_size = 1000
        self.d_model = 128
        self.max_len = 64
        
        self.config = MiniGPTConfig(
            vocab_size=self.vocab_size,
            d_model=self.d_model,
            num_heads=4,
            d_ff=512,
            num_layers=2,
            max_sequence_length=self.max_len
        )
        self.model = MiniGPT(self.config)

    def test_output_shape(self):
        """[x] Output shape matching (batch, sequence, vocab_size)"""
        x = torch.randint(0, self.vocab_size, (2, 10))
        logits = self.model(x)
        assert logits.shape == (2, 10, self.vocab_size)

    def test_batch_size_equals_one(self):
        """[x] Batch size = 1 tracking"""
        x = torch.randint(0, self.vocab_size, (1, 15))
        logits = self.model(x)
        assert logits.shape[0] == 1

    def test_batch_size_greater_than_one(self):
        """[x] Batch size > 1 tracking"""
        x = torch.randint(0, self.vocab_size, (4, 15))
        logits = self.model(x)
        assert logits.shape[0] == 4

    def test_short_sequence(self):
        """[x] Short sequence processing"""
        x = torch.randint(0, self.vocab_size, (2, 1))
        logits = self.model(x)
        assert logits.shape[1] == 1

    def test_maximum_sequence_length(self):
        """[x] Maximum sequence length capacity limit"""
        x = torch.randint(0, self.vocab_size, (2, self.max_len))
        logits = self.model(x)
        assert logits.shape[1] == self.max_len

    def test_sequence_length_exceeds_max_raises_value_error(self):
        """[x] Sequence length > max_sequence_length raises ValueError"""
        x = torch.randint(0, self.vocab_size, (2, self.max_len + 1))
        with pytest.raises(ValueError):
            self.model(x)

    def test_invalid_configuration_raises_value_error(self):
        """[x] Invalid configuration raises ValueError"""
        # 128 d_model is not evenly divisible by 5 heads
        with pytest.raises(ValueError):
            MiniGPTConfig(vocab_size=1000, d_model=128, num_heads=5)

    def test_gradients_reach_all_components(self):
        """
        [x] Gradients reach token embeddings
        [x] Gradients reach positional embeddings
        [x] Gradients reach Transformer blocks
        [x] Gradients reach final LayerNorm
        [x] Gradients reach LM head
        """
        x = torch.randint(0, self.vocab_size, (2, 10))
        logits = self.model(x)
        loss = logits.mean()
        loss.backward()
        
        # 1. Verify Entry Interface Embeddings Gradients
        assert self.model.token_embedding.weight.grad is not None
        assert torch.isfinite(self.model.token_embedding.weight.grad).all()
        
        assert self.model.position_embedding.weight.grad is not None
        assert torch.isfinite(self.model.position_embedding.weight.grad).all()
        
        # 2. Verify Deep Core Processing Transformer Block Gradients
        for block in self.model.blocks:
            assert block.mha.Wq.weight.grad is not None
            assert torch.isfinite(block.mha.Wq.weight.grad).all()
            assert block.ffn.w_1.weight.grad is not None
            assert torch.isfinite(block.ffn.w_1.weight.grad).all()
            
        # 3. Verify Final Normalization Boundary Gradients
        assert self.model.final_layer_norm.weight.grad is not None
        assert torch.isfinite(self.model.final_layer_norm.weight.grad).all()
        
        # 4. Verify Output Projection Interface Head Gradients
        assert self.model.lm_head.weight.grad is not None
        assert torch.isfinite(self.model.lm_head.weight.grad).all()
