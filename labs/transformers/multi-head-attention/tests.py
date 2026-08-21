import unittest
import torch
import inspect
from multi_head_attention import MultiHeadAttention as mha

class TestMultiHeadAttention(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(42)
        self.batch_size = 2
        self.seq_len = 4
        self.d_model = 8
        self.x = torch.randn(self.batch_size, self.seq_len, self.d_model)

    def _run_forward(self, model, mask=None):
        """Helper to call forward correctly regardless of its signature."""
        sig = inspect.signature(model.forward)
        # Check how many positional/keyword parameters forward accepts (excluding self and mask)
        params = [p for p in sig.parameters.values() if p.name not in ('self', 'mask', 'args', 'kwargs')]
        
        kwargs = {}
        if mask is not None and 'mask' in sig.parameters:
            kwargs['mask'] = mask

        if len(params) >= 3:
            return model(self.x, self.x, self.x, **kwargs)
        else:
            return model(self.x, **kwargs)

    def test_output_shape_matches_input_shape(self):
        """[x] Output shape matches input shape"""
        model = mha(d_model=self.d_model, num_heads=2)
        output, _ = self._run_forward(model)
        self.assertEqual(output.shape, self.x.shape)

    def test_not_divisible_raises_value_error(self):
        """[x] d_model not divisible by num_heads raises ValueError"""
        with self.assertRaises(ValueError):
            mha(d_model=8, num_heads=3)

    def test_one_head_works(self):
        """[x] One head works"""
        model = mha(d_model=self.d_model, num_heads=1)
        output, attn_weights = self._run_forward(model)
        self.assertEqual(output.shape, self.x.shape)
        self.assertEqual(attn_weights.shape[1], 1)

    def test_multiple_heads_work(self):
        """[x] Multiple heads work"""
        model = mha(d_model=self.d_model, num_heads=4)
        output, attn_weights = self._run_forward(model)
        self.assertEqual(output.shape, self.x.shape)
        self.assertEqual(attn_weights.shape[1], 4)

    def test_attention_weights_shape(self):
        """[x] Attention weights have shape: (batch, heads, seq_len, seq_len)"""
        num_heads = 2
        model = mha(d_model=self.d_model, num_heads=num_heads)
        _, attn_weights = self._run_forward(model)
        expected_shape = (self.batch_size, num_heads, self.seq_len, self.seq_len)
        self.assertEqual(attn_weights.shape, expected_shape)

    def test_attention_row_sums_to_one(self):
        """[x] Every attention row sums to approximately 1"""
        model = mha(d_model=self.d_model, num_heads=2)
        _, attn_weights = self._run_forward(model)
        
        row_sums = attn_weights.sum(dim=-1)
        expected_sums = torch.ones_like(row_sums)
        self.assertTrue(torch.allclose(row_sums, expected_sums, atol=1e-6))

    def test_causal_masking_blocks_future(self):
        """[x] Causal masking blocks future tokens"""
        model = mha(d_model=self.d_model, num_heads=2)
        causal_mask = torch.tril(torch.ones(self.seq_len, self.seq_len))
        
        _, attn_weights = self._run_forward(model, mask=causal_mask)
        
        future_attention = torch.triu(attn_weights, diagonal=1)
        zeros = torch.zeros_like(future_attention)
        self.assertTrue(torch.allclose(future_attention, zeros, atol=1e-6))

    def test_gradients_flow_through_module(self):
        """[x] Gradients can flow through the module"""
        model = mha(d_model=self.d_model, num_heads=2)
        x = self.x.clone().requires_grad_(True)
        
        # Override self.x temporarily for the helper to track gradients cleanly
        original_x = self.x
        self.x = x
        try:
            output, _ = self._run_forward(model)
        finally:
            self.x = original_x

        loss = output.sum()
        loss.backward()
        
        self.assertIsNotNone(x.grad)
        
        # Agnostic check: ensures every linear layer weight gets trained
        has_weights = False
        for name, param in model.named_parameters():
            if "weight" in name:
                has_weights = True
                self.assertIsNotNone(param.grad, f"Parameter layer '{name}' failed to accumulate gradients.")
                self.assertTrue(torch.isfinite(param.grad).all())
        
        self.assertTrue(has_weights, "No weights found in the model to test gradients on.")
        print("\nGradient Verification: All parameter layers successfully received training gradients!")

if __name__ == "__main__":
    unittest.main()
