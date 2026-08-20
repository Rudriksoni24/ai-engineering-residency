import sys
from pathlib import Path
import torch

CURRENT_DIR = Path(__file__).resolve().parent
LABS_ROOT = CURRENT_DIR.parent.parent
Tokenizer_dir = LABS_ROOT / "tokenizer" / "tokenizer-from-scratch"
ROUND_TRIP_DIR = LABS_ROOT / "tokenizer" / "tests"  

# Inject directories at the absolute front of Python's search path
for directory in [Tokenizer_dir, ROUND_TRIP_DIR, CURRENT_DIR]:
    if directory.exists() and str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

# 2. Attempt explicit imports with direct error tracking
try:
    from tokenizer import SimpleTokenizer
    print("🎯 Successfully imported SimpleTokenizer from tokenizer-from-scratch!")
except ImportError:
    try:
        from round_trip_test import SpecialTokenizer as SimpleTokenizer
        print("🎯 Successfully imported SpecialTokenizer from round-trip script!")
    except ImportError:
        raise ImportError(
            f"\n❌ Could not locate your tokenizer script.\n"
            f"Please verify your files exist in one of these locations:\n"
            f"  - {Tokenizer_dir}/tokenizer.py\n"
            f"  - {ROUND_TRIP_DIR}/round_trip_test.py"
        )

class RandomEmbeddingLookup:
    def __init__(self, dataset_path: str, embedding_dim: int = 64):
        self.tokenizer = SimpleTokenizer()
        path = Path(dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Missing dataset at {path.resolve()}")

        self.tokenizer.build_vocab(path)
        self.vocab_size = len(self.tokenizer.token_to_id)
        self.embedding_dim = embedding_dim
        self.embedding_matrix = torch.randn(self.vocab_size, self.embedding_dim)

        print(f"📊 Vocabulary Size: {self.vocab_size}")
        print(f"📦 Matrix Dimension: {self.vocab_size} x {self.embedding_dim}\n")

    def lookup_word(self, word: str) -> torch.Tensor:
        clean_word = word.strip().lower()
        token_id = self.tokenizer.token_to_id.get(clean_word, 1)
        return self.embedding_matrix[token_id]

    def lookup_id(self, token_id:int) -> torch.Tensor:
        if token_id < 0 or token_id >= self.vocab_size:
            raise IndexError(f"Token ID {token_id} is out of bounds for vocabulary size {self.vocab_size}.")
        return self.embedding_matrix[token_id]

    def lookup_sentence(self, sentence: str) -> torch.Tensor:
        token_ids = self.tokenizer.encode(sentence)
        input_tensor = torch.tensor(token_ids, dtype=torch.long)
        return self.embedding_matrix[input_tensor]
    
    def find_closest_words(self, target_word: str, top_k: int = 3):
        """
        Computes the cosine similarity between the target word's embedding 
        and every other word vector in the entire vocabulary.
        """
        target_word = target_word.strip().lower()
        if target_word not in self.tokenizer.token_to_id:
            print(f"⚠️ '{target_word}' not found in vocabulary! Using <UNK> vector instead.")
            target_id = 1
        else:
            target_id = self.tokenizer.token_to_id[target_word]

        # 1. Extract the target word's vector. Shape: (Embedding Dim,)
        target_vector = self.embedding_matrix[target_id]

        # 2. Normalize vectors to make math invariant to scale (unit length = 1.0)
        # Adding a tiny epsilon (1e-9) avoids any potential division-by-zero errors
        target_norm = target_vector / (target_vector.norm() + 1e-9)
        matrix_norms = self.embedding_matrix / (self.embedding_matrix.norm(dim=-1, keepdim=True) + 1e-9)

        # 3. Compute Cosine Similarity via high-speed dot product multiplication
        # Shape: (Vocabulary Size,)
        similarities = torch.matmul(matrix_norms, target_norm)

        # 4. Sort indices in descending order of similarity score
        sorted_indices = torch.argsort(similarities, descending=True)

        print(f"🔎 Closest words to '{target_word}':")
        print("-" * 40)
        
        count = 0
        for idx in sorted_indices:
            idx_item = idx.item()
            word = self.tokenizer.id_to_token[idx_item]
            
            # Skip the target word itself so it doesn't match with itself at 1.0000
            if word == target_word:
                continue
                
            score = similarities[idx_item].item()
            print(f"Rank {count+1}: Score = {score:.4f} | Word: '{word}'")
            
            count += 1
            if count >= top_k:
                break
        print("\n")


if __name__ == "__main__":
    dataset_file = Tokenizer_dir / "dataset.txt" if (Tokenizer_dir / "dataset.txt").exists() else Path("dataset.txt")

    lookup_system = RandomEmbeddingLookup(dataset_file, embedding_dim=64)

    print("===1. Word Lookup ===")
    word_vec = lookup_system.lookup_word("Kubernetes")
    print(f"Word Vector for 'Kubernetes': {word_vec}\n")

    print("===2. ID Lookup ===")
    bos_vec = lookup_system.lookup_id(2)
    print(f"Token ID 2 (<BOS>) -> Vector shape: {bos_vec.shape}\n")

    print("===3. Sentence Lookup ===")
    test_sentence = "Python drives AI pipelines smoothly."
    sentence_matrix = lookup_system.lookup_sentence(test_sentence)
    print(f"Sentence: \"{test_sentence}\"")
    print(f"Resulting Output Shape: {sentence_matrix.shape} (Tokens x Embedding Dim)")

    first_token_id = lookup_system.tokenizer.encode(test_sentence)[0]
    expected_first_vector = lookup_system.lookup_id(first_token_id)

    assert torch.equal(sentence_matrix[0], expected_first_vector), "Sequence boundary tracking mismatch!"
    print("\n Verification successful! All matrix lookup hooks operate as expected. ✅")

        # Target search words provided
    test_words = ["bank", "money", "finance", "loan", "apple", "orange", "swift"]
    
    print("=== Running Search across Vocabulary ===")
    for word in test_words:
        lookup_system.find_closest_words(target_word=word, top_k=2)



# def create_embedding_pipeline():
#     tokenizer = SimpleTokenizer()

#     dataset_path = LABS_ROOT / "tokenizer" / "tokenizer-from-scratch" / "dataset.txt"
#     if not dataset_path.exists():
#         dataset_path = Path("dataset.txt")
        
#     if not dataset_path.exists():
#         raise FileNotFoundError(f"Could not find dataset.txt at {dataset_path.resolve()}. Please check the path.")
    
#     tokenizer.build_vocab(dataset_path)
    
#     vocab_size = len(tokenizer.token_to_id)
#     Embedding_dim = 64

#     print(f"\n📊 Vocabulary Size determined from disk: {vocab_size}")
#     print(f"📐 Target Embedding Dimension size: {Embedding_dim}")

#     embedding_matrix = torch.randn(vocab_size, Embedding_dim)
#     print(f"📦 Embedding Matrix initialized successfully! Shape: {embedding_matrix.shape}")

#     sample_phrase = "Tesla build microservices"
#     token_ids = tokenizer.encode(sample_phrase)
#     print(f'\n📝 Sample Input: "{sample_phrase}"')
#     print(f"🆔 Generated Token IDs: {token_ids}")

#     input_tensor = torch.tensor(token_ids, dtype= torch.long)

#     phrase_embeddings = embedding_matrix[input_tensor]
#     print(f"🚀 Output Dense Matrix Shape: {phrase_embeddings.shape} (Tokens x Embedding Dim)")
    
#     print(f"\n✨ Embedding Vector for the first token ID ({token_ids[0]}):")
#     print(phrase_embeddings[0])

# if __name__ == "__main__":
#     create_embedding_pipeline()