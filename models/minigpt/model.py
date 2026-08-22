import os
import sys
import torch
import torch.nn as nn
from models.minigpt.config import MiniGPTConfig

# Resolve relative paths to import Week 2 Day 3 TransformerBlock dynamically
current_file_path = os.path.abspath(__file__)
root_repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
transformer_block_dir = os.path.join(root_repo_dir, "labs", "transformers", "transformer-block")

if transformer_block_dir not in sys.path:
    sys.path.insert(0, transformer_block_dir)

from transformer_block import TransformerBlock

class MiniGPT(nn.Module):
    def __init__(self, config: MiniGPTConfig):
        super().__init__()
        self.config = config

        # Input projection embedding lookup layers
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.position_embedding = nn.Embedding(config.max_sequence_length, config.d_model)

        # Main processing stack with individual, un-shared transformer block layers
        self.blocks = nn.ModuleList([
            TransformerBlock(
                d_model=config.d_model,
                num_heads=config.num_heads,
                d_ff=config.d_ff,
                dropout=0.1
            )
            for _ in range(config.num_layers)
        ])

        # Final structural layer norm boundary prior to predicting logits
        self.final_layer_norm = nn.LayerNorm(config.d_model)

        # Language Model projection head maps deep states back to word scores
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        batch_size, sequence_length = input_ids.shape

        # 1. Validate sequence length context limits
        if sequence_length > self.config.max_sequence_length:
            raise ValueError(
                f"Input sequence length ({sequence_length}) exceeds configured "
                f"max_sequence_length ({self.config.max_sequence_length})"
            )

        # 2. Create position IDs dynamically matching the execution target device
        position_ids = torch.arange(sequence_length, device=input_ids.device)

        # 3. Token embeddings
        tok_emb = self.token_embedding(input_ids)

        # 4. Position embeddings
        pos_emb = self.position_embedding(position_ids)

        # 5. Combine (Broadcast addition across batch dimension)
        x = tok_emb + pos_emb

        # 6. Create causal mask instruction configuration
        # Instructs the sub-blocks to trigger your Day 1/Day 2 causal mask function natively
        causal_mask = "causal"

        # 7. Pass through Transformer blocks sequentially
        for block in self.blocks:
            x = block(x, mask=causal_mask)

        # 8. Final LayerNorm stabilization
        x = self.final_layer_norm(x)

        # 9. Vocabulary logits projection interface map
        logits = self.lm_head(x)

        return logits
