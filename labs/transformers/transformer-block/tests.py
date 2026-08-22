import pytest
import torch
import torch.nn as nn
from transformer_block import TransformerBlock

class TestTransformerBlock:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        torch.manual_seed(42)
        self.batch_size = 2
        self.seq_len = 10
        self.d_model = 512
        self.num_heads = 8
        self.d_ff = 2048
        self.x = torch.randn(self.batch_size, self.seq_len, self.d_model)

    def test_input_output_shape_preserved(self):
        """[x] Input/output shape preserved"""
        model = TransformerBlock(d_model=self.d_model, num_heads=self.num_heads, d_ff=self.d_ff)
        output = model(self.x)
        assert output.shape == self.x.shape

    def test_ffn_expands_d_model_to_d_ff(self):
        """[x] FFN expands d_model → d_ff"""
        model = TransformerBlock(d_model=self.d_model, num_heads=self.num_heads, d_ff=self.d_ff)
        # Check out_features of the first linear expansion layer inside your FFN component
        assert model.ffn.w_1.out_features == self.d_ff

    def test_ffn_contracts_d_ff_to_d_model(self):
        """[x] FFN contracts d_ff → d_model"""
        model = TransformerBlock(d_model=self.d_model, num_heads=self.num_heads, d_ff=self.d_ff)
        # Check out_features of the second linear compression layer inside your FFN component
        assert model.ffn.w_2.out_features == self.d_model

    def test_transformer_block_works_with_batch_greater_than_one(self):
        """[x] Transformer block works with batch > 1"""
        assert self.batch_size > 1
        model = TransformerBlock(d_model=self.d_model, num_heads=self.num_heads, d_ff=self.d_ff)
        output = model(self.x)
        assert output.shape[0] == self.batch_size

    def test_transformer_block_works_with_sequence_greater_than_one(self):
        """[x] Transformer block works with sequence > 1"""
        assert self.seq_len > 1
        model = TransformerBlock(d_model=self.d_model, num_heads=self.num_heads, d_ff=self.d_ff)
        output = model(self.x)
        assert output.shape[1] == self.seq_len

    def test_causal_mask_passed_through_correctly(self):
        """[x] Causal mask is passed through correctly"""
        model = TransformerBlock(d_model=self.d_model, num_heads=self.num_heads, d_ff=self.d_ff)
        
        # Passing 'causal' down into the forward wrapper should evaluate without raising an exception
        try:
            output = model(self.x, mask="causal")
            assert output.shape == self.x.shape
        except Exception as e:
            pytest.fail(f"Passing mask='causal' raised an unexpected exception: {e}")

    def test_gradients_exist_after_backward(self):
        """[x] Gradients exist after backward()"""
        model = TransformerBlock(d_model=self.d_model, num_heads=self.num_heads, d_ff=self.d_ff)
        x_track = self.x.clone().requires_grad_(True)
        
        output = model(x_track, mask="causal")
        loss = output.mean()
        loss.backward()
        
        # Verify continuous graph tracking back to input node
        assert x_track.grad is not None
        
        # Verify backpropagation flow registered across all expected parameter tracks
        targets = [model.mha.Wq, model.mha.Wk, model.mha.Wv, model.mha.Wo, model.ffn.w_1, model.ffn.w_2, model.norm1, model.norm2]
        for layer in targets:
            assert layer.weight.grad is not None
            assert torch.isfinite(layer.weight.grad).all()

    def test_all_expected_trainable_parameters_exist(self):
        """[x] All expected trainable parameters exist"""
        model = TransformerBlock(d_model=self.d_model, num_heads=self.num_heads, d_ff=self.d_ff)
        
        # Collect parameter keys present in named tracks
        param_names = [name for name, _ in model.named_parameters()]
        
        expected_substrings = [
            "mha.Wq.weight", "mha.Wk.weight", "mha.Wv.weight", "mha.Wo.weight",
            "ffn.w_1.weight", "ffn.w_1.bias", "ffn.w_2.weight", "ffn.w_2.bias",
            "norm1.weight", "norm1.bias", "norm2.weight", "norm2.bias"
        ]
        
        for expected in expected_substrings:
            assert any(expected in name for name in param_names), f"Missing target parameter track: {expected}"

    def test_invalid_attention_configuration_raises_error(self):
        """[x] Invalid attention configuration raises an error"""
        # 512 is not evenly divisible by 7 heads
        with pytest.raises(ValueError):
            TransformerBlock(d_model=512, num_heads=7, d_ff=2048)
