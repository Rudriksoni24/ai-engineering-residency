from dataclasses import dataclass

@dataclass
class MiniGPTConfig:
    vocab_size: int
    d_model: int = 128
    num_heads: int = 4
    d_ff: int = 512
    num_layers: int = 4
    max_sequence_length: int = 64

    def __post_init__(self):
        # 1. Base Parameter Group Validation
        if self.vocab_size <= 0:
            raise ValueError("vocab_size must be greater than 0")

        if self.d_model <= 0:
            raise ValueError("d_model must be greater than 0")

        # 2. Structural Attention Divisibility Validation
        if self.num_heads <= 0:
            raise ValueError("num_heads must be greater than 0")

        if self.d_model % self.num_heads != 0:
            raise ValueError(
                f"d_model ({self.d_model}) must be evenly divisible by num_heads ({self.num_heads})"
            )

        # 3. Remaining Layer, FFN, and Sequence Context Validation
        if self.d_ff <= 0:
            raise ValueError("d_ff must be greater than 0")

        if self.num_layers <= 0:
            raise ValueError("num_layers must be greater than 0")

        if self.max_sequence_length <= 0:
            raise ValueError("max_sequence_length must be greater than 0")


# --- Local Verification Script ---
if __name__ == "__main__":
    print("Testing valid configuration creation...")
    config = MiniGPTConfig(vocab_size=5000)
    print(f"✔ Success! Configuration initialized: {config}")

    print("\nTesting validation constraint guards...")
    
    # Test invalid layer bounds
    try:
        MiniGPTConfig(vocab_size=5000, num_layers=0)
    except ValueError as e:
        print(f"✔ Caught expected error: {e}")

    # Test invalid attention breakdown dimensions
    try:
        MiniGPTConfig(vocab_size=5000, d_model=128, num_heads=5)
    except ValueError as e:
        print(f"✔ Caught expected error: {e}")
