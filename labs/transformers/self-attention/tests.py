import math
import pytest
import torch

# Import your implementations from the attention lab module
from attention import (
    softmax,
    scaled_dot_product_attention,
    create_causal_mask
)

# -------------------------------------------------------------------------
# Test 1 & 2: Softmax Properties & Numerical Stability
# -------------------------------------------------------------------------
def test_softmax_sums_to_one():
    """1. Verifies that the stable softmax output elements sum to exactly 1.0."""
    x = torch.tensor([1.0, 2.0, 3.0, 4.0])
    probs = softmax(x, dim=-1)
    
    assert torch.isclose(probs.sum(), torch.tensor(1.0)), "Softmax probabilities must sum to 1.0"

def test_stable_softmax_large_values():
    """2. Verifies that subtracting max(x) prevents NaN/inf on extreme inputs."""
    # Large values would trigger infinity overflow (inf) in vanilla softmax
    large_x = torch.tensor([1000.0, 1001.0, 1002.0])
    
    try:
        probs = softmax(large_x, dim=-1)
    except Exception as e:
        pytest.fail(f"Stable softmax crashed on large inputs: {e}")
        
    assert not torch.isnan(probs).any(), "Stable softmax output contains NaN values!"
    assert not torch.isinf(probs).any(), "Stable softmax output contains Infinity values!"
    # Ensure largest element still maintains highest probability relative weight
    assert probs[2] > probs[0]

# -------------------------------------------------------------------------
# Test 3, 4 & 5: Attention Output Properties
# -------------------------------------------------------------------------
@pytest.fixture
def dummy_attention_inputs():
    """Fixture providing standard deterministic tensor dimensions for validation."""
    torch.manual_seed(42)
    seq_len = 4
    d_model = 8
    Q = torch.randn(seq_len, d_model)
    K = torch.randn(seq_len, d_model)
    V = torch.randn(seq_len, d_model)
    return Q, K, V, seq_len, d_model

def test_attention_output_shape(dummy_attention_inputs):
    """3. Verifies attention context matrix matches shape: (seq_len, d_model)."""
    Q, K, V, seq_len, d_model = dummy_attention_inputs
    output, _ = scaled_dot_product_attention(Q, K, V)
    
    assert output.shape == (seq_len, d_model), f"Expected output shape {(seq_len, d_model)}, got {output.shape}"

def test_attention_weights_shape(dummy_attention_inputs):
    """4. Verifies attention routing matrix matches shape: (seq_len, seq_len)."""
    Q, K, V, seq_len, _ = dummy_attention_inputs
    _, weights = scaled_dot_product_attention(Q, K, V)
    
    assert weights.shape == (seq_len, seq_len), f"Expected weights shape {(seq_len, seq_len)}, got {weights.shape}"

def test_attention_rows_sum_to_one(dummy_attention_inputs):
    """5. Verifies each structural query row creates a valid probability distribution."""
    Q, K, V, _, _ = dummy_attention_inputs
    _, weights = scaled_dot_product_attention(Q, K, V)
    
    # Sum along rows axis (dim=-1)
    row_sums = weights.sum(dim=-1)
    expected_sums = torch.ones_like(row_sums)
    
    assert torch.allclose(row_sums, expected_sums), "Every row index in the attention weights matrix must sum to 1.0"

# -------------------------------------------------------------------------
# Test 6 & 7: Causal Masking Controls
# -------------------------------------------------------------------------
def test_causal_mask_blocks_future():
    """6. Verifies causal mask generation builds a lower-triangular matrix configuration."""
    seq_len = 4
    mask = create_causal_mask(seq_len)
    
    # Expected: 1s on/below diagonal, 0s strictly above the diagonal
    expected_mask = torch.tril(torch.ones(seq_len, seq_len))
    
    assert torch.equal(mask, expected_mask), "Causal mask must match lower triangular framework layout"

def test_future_masked_probabilities_are_zero(dummy_attention_inputs):
    """7. Verifies future masked score slots result in an attention weight of approximately 0.0."""
    Q, K, V, seq_len, _ = dummy_attention_inputs
    mask = create_causal_mask(seq_len)
    
    _, weights = scaled_dot_product_attention(Q, K, V, mask=mask)
    
    # Above the diagonal elements must be forced completely to zero
    for i in range(seq_len):
        for j in range(i + 1, seq_len):
            assert torch.isclose(weights[i, j], torch.tensor(0.0), atol=1e-6), \
                f"Future leak detected! Row {i} managed to look forward at Column {j} with weight {weights[i, j].item()}"
