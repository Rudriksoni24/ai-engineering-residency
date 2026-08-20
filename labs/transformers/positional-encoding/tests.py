import pytest
import torch
from positional_encoding import positional_encoding

# -------------------------------------------------------------------------
# Test 1: Verification of Correct Matrix Output Shapes
# -------------------------------------------------------------------------
def test_correct_shape():
    """Verifies that the generated matrix perfectly matches configured sequence length and model dimensions."""
    seq_len = 24
    d_model = 128
    pe = positional_encoding(sequence_length=seq_len, d_model=d_model)
    
    assert pe.shape == (seq_len, d_model), f"Expected shape {(seq_len, d_model)}, but got {pe.shape}"

# -------------------------------------------------------------------------
# Test 2: Verification that Distinct Positions Have Unique Vectors
# -------------------------------------------------------------------------
def test_position_uniqueness():
    """Ensures position 0 differs from position 1 so the network can uniquely identify item ordering."""
    seq_len = 10
    d_model = 64
    pe = positional_encoding(sequence_length=seq_len, d_model=d_model)
    
    pos_0_vector = pe[0]
    pos_1_vector = pe[1]
    
    # Check that they are not completely identical arrays
    assert not torch.equal(pos_0_vector, pos_1_vector), "Failed: Position 0 and Position 1 have identical vector fingerprints!"

# -------------------------------------------------------------------------
# Test 3: Verification of Absolute Output Determinism
# -------------------------------------------------------------------------
def test_output_determinism():
    """Validates that two separate calls with identical arguments yield perfectly identical tensors."""
    seq_len = 32
    d_model = 256
    
    pe_run_first = positional_encoding(sequence_length=seq_len, d_model=d_model)
    pe_run_second = positional_encoding(sequence_length=seq_len, d_model=d_model)
    
    assert torch.equal(pe_run_first, pe_run_second), "Failed: Encodings are not deterministic across distinct pipeline calls."

# -------------------------------------------------------------------------
# Test 4: Verification that Changing d_model Appropriately Mutates Shape
# -------------------------------------------------------------------------
@pytest.mark.parametrize("dynamic_d_model", [32, 64, 128, 512])
def test_different_d_model_changes_shape(dynamic_d_model):
    """Ensures modifying the d_model structural size changes output dimensions dynamically without hardcoding bugs."""
    seq_len = 15
    pe = positional_encoding(sequence_length=seq_len, d_model=dynamic_d_model)
    
    assert pe.shape == (seq_len, dynamic_d_model)

# -------------------------------------------------------------------------
# Test 5: Mathematical Compatibility with an Embedding Matrix Matrix Addition
# -------------------------------------------------------------------------
def test_embedding_addition_compatibility():
    """Confirms positional encodings can be directly added element-wise to standard token embedding lookups."""
    seq_len = 5
    d_model = 64
    
    # Mock a standard look-up table or batch tensor token sequence representation
    simulated_embeddings = torch.randn(seq_len, d_model)
    pe = positional_encoding(sequence_length=seq_len, d_model=d_model)
    
    # Attempt programmatic element-wise tensor addition
    try:
        position_aware_space = simulated_embeddings + pe
    except Exception as e:
        pytest.fail(f"Failed to combine token embedding rows with positional values: {e}")
        
    assert position_aware_space.shape == (seq_len, d_model), "Resulting position-aware space shape was distorted during tensor calculation."
