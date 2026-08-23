import torch
from torch.utils.data import Dataset

class NextTokenDataset(Dataset):
    def __init__(self, token_ids: list[int], sequence_length: int):
        """
        Custom PyTorch Dataset designed to slice a raw token stream into 
        next-token prediction tensor matching pairs.
        """
        # Ensure that the dataset can construct at least one complete offset chunk pairs
        if len(token_ids) <= sequence_length:
            raise ValueError(
                f"Total token stream length ({len(token_ids)}) must be strictly greater "
                f"than the requested sequence_length ({sequence_length}) to construct targets."
            )
            
        self.token_ids = torch.tensor(token_ids, dtype=torch.long)
        self.sequence_length = sequence_length

    def __len__(self) -> int:
        """
        Returns the total count of valid sequence chunks available in the token stream.
        """
        return len(self.token_ids) - self.sequence_length

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Pulls a matching pair at a specific index offset index location.
        Returns:
            input_ids:  Tensor of shape (sequence_length,)
            target_ids: Tensor of shape (sequence_length,) shifted right by exactly 1 position
        """
        # Slice target block window from index idx
        input_ids = self.token_ids[idx : idx + self.sequence_length]
        
        # Slice overlapping target block window shifted forward by exactly 1 token position
        target_ids = self.token_ids[idx + 1 : idx + self.sequence_length + 1]
        
        return input_ids, target_ids


# --- Local Verification Script ---
if __name__ == "__main__":
    print("=== Next-Token Dataset Diagnostic Validation ===")
    
    # Task 2 Challenge parameters configuration
    challenge_token_ids = [10, 21, 7, 3, 15, 8]
    context_length = 4
    
    # 1. Instantiate dataset module
    dataset = NextTokenDataset(token_ids=challenge_token_ids, sequence_length=context_length)
    print(f"✔ Dataset initialized successfully. Total items parsed: {len(dataset)}")
    
    # 2. Extract and display item sample index 0
    input_sample, target_sample = dataset[0]
    
    print("\n--- Slice Sample Offset Index 0 Trace ---")
    print(f"Input Tensor  (input_ids) : {input_sample.tolist()} | Shape: {tuple(input_sample.shape)}")
    print(f"Target Tensor (target_ids): {target_sample.tolist()} | Shape: {tuple(target_sample.shape)}")
    
    # 3. Explicit Target Verification Assertions
    expected_input = [10, 21, 7, 3]
    expected_target = [21, 7, 3, 15]
    
    assert input_sample.tolist() == expected_input, f"Expected input {expected_input}, got {input_sample.tolist()}"
    assert target_sample.tolist() == expected_target, f"Expected target {expected_target}, got {target_sample.tolist()}"
    assert input_sample.shape == (context_length,) and target_sample.shape == (context_length,)
    
    print("\n🎉 SUCCESS: Data slicing matches specified shifted sequence invariants perfectly!")
