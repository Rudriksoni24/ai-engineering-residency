import sys
from pathlib import Path
import torch

# 1. Path setups to import your reusable tokenizer
CURRENT_DIR = Path(__file__).resolve().parent
LABS_ROOT = CURRENT_DIR.parent.parent  

TOKENIZER_DIR = LABS_ROOT / "tokenizer" / "tokenizer-from-scratch"
if TOKENIZER_DIR.exists() and str(TOKENIZER_DIR) not in sys.path:
    sys.path.insert(0, str(TOKENIZER_DIR))

try:
    from tokenizer import SimpleTokenizer
except ImportError:
    from round_trip_test import SpecialTokenizer as SimpleTokenizer


class RandomEmbeddingLookup:
    def __init__(self, dataset_path: str, embedding_dim: int = 64):
        """
        Loads the tokenizer from the dataset, computes vocabulary size,
        and initializes a random PyTorch embedding matrix lookup table.
        """
        self.tokenizer = SimpleTokenizer()
        path = Path(dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Missing dataset at {path.resolve()}")
            
        self.tokenizer.build_vocab(path)
        self.vocab_size = len(self.tokenizer.token_to_id)
        self.embedding_dim = embedding_dim
        
        # Initialize Random Embedding Matrix (Vocab Size x Embedding Dim)
        self.embedding_matrix = torch.randn(self.vocab_size, self.embedding_dim)
        print(f"📊 Vocabulary Size: {self.vocab_size} | Matrix Dimension: {self.vocab_size} x {self.embedding_dim}\n")

    def lookup_sentence(self, sentence: str) -> torch.Tensor:
        """
        Converts a full string sentence into a sequence tensor of vectors.
        Output Shape: (Sequence Length, Embedding Dimension)
        """
        token_ids = self.tokenizer.encode(sentence)
        input_tensor = torch.tensor(token_ids, dtype=torch.long)
        return self.embedding_matrix[input_tensor]

    def get_sentence_embedding(self, sentence: str) -> torch.Tensor:
        """
        Computes a single sentence embedding vector by calculating the element-wise 
        average (mean pooling) of all word embeddings in the sentence.
        
        Output Shape: (Embedding Dimension,)
        """
        # Step 1: Retrieve individual token vectors. Shape: (Sequence Length, Embedding Dim)
        word_vectors = self.lookup_sentence(sentence)
        
        if word_vectors.shape[0] == 0:
            # Handle empty sentence edge case cleanly by returning a zero vector
            return torch.zeros(self.embedding_dim)
            
        # Step 2: Compute the average across the token dimension (axis/dim 0)
        # Shape transforms from (Sequence Length, 64) -> (64,)
        sentence_vector = torch.mean(word_vectors, dim=0)
        return sentence_vector


# --- Execution and Sentence Pooling Verification Loop ---
if __name__ == "__main__":
    dataset_file = TOKENIZER_DIR / "dataset.txt" if (TOKENIZER_DIR / "dataset.txt").exists() else Path("dataset.txt")
    
    # Initialize the lookup system
    lookup_system = RandomEmbeddingLookup(dataset_path=dataset_file, embedding_dim=64)
    
    # Define our test sentence
    phrase = "Machine Learning"
    print(f"📝 Input Text: \"{phrase}\"")
    
    # 1. Fetch individual word vectors
    token_matrix = lookup_system.lookup_sentence(phrase)
    print(f"1. Individual Token Matrix Shape: {token_matrix.shape} (Tokens x Features)")
    
    # 2. Compute the pooled average sentence vector
    pooled_vector = lookup_system.get_sentence_embedding(phrase)
    print(f"2. Final Pooled Sentence Embedding Vector Shape: {pooled_vector.shape}")
    
    # 3. Mathematical Verification Check
    # Verify that manually adding the rows and dividing matches our function output
    manual_average = (token_matrix[0] + token_matrix[1]) / 2.0
    
    print("-" * 55)
    if torch.allclose(pooled_vector, manual_average, atol=1e-5):
        print("✅ SUCCESS: Sentence pooling average calculated perfectly!")
        print("\n✨ Generated Sentence Embedding Vector Snippet:")
        print(pooled_vector[:5])  # Show the first 5 numbers of our dense sentence representation
    else:
        print("❌ FAILURE: Math mismatch in pooling extraction logic.")
