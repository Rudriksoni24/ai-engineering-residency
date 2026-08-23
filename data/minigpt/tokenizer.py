class CharTokenizer:
    def __init__(self, unk_token: str = "?"):
        """
        A character-level tokenizer that explicitly handles unknown characters.
        The unk_token must be a single visible character (default: "?").
        """
        if len(unk_token) != 1:
            raise ValueError(f"For a character tokenizer, unk_token must be exactly 1 character long. Got length {len(unk_token)}")
            
        self.unk_token = unk_token
        self.chars = []
        self.char_to_id = {}
        self.id_to_char = {}
        self.is_fitted = False

    def fit(self, text: str):
        """
        Builds the vocabulary mapping ensuring the unk_token is explicitly included.
        """
        unique_chars = set(text) if text else set()
        
        # Explicitly inject the single-character unk_token into the set
        unique_chars.add(self.unk_token)
        
        # Sort to keep vocabulary ordering deterministic
        self.chars = sorted(list(unique_chars))
        self.char_to_id = {char: i for i, char in enumerate(self.chars)}
        self.id_to_char = {i: char for i, char in enumerate(self.chars)}
        self.is_fitted = True
        return self

    def encode(self, text: str) -> list[int]:
        """
        Converts a raw string of text into a list of integer token IDs.
        """
        if not self.is_fitted:
            raise RuntimeError("Tokenizer must be fitted using `.fit(text)` before encoding.")
            
        if not text:
            return []

        encoded_ids = []
        for char in text:
            if char in self.char_to_id:
                encoded_ids.append(self.char_to_id[char])
            else:
                # Fallback safely to the explicitly mapped unknown token ID
                encoded_ids.append(self.char_to_id[self.unk_token])
                
        return encoded_ids

    def decode(self, token_ids: list[int]) -> str:
        """
        Converts a list of integer token IDs back into a readable string.
        """
        if not self.is_fitted:
            raise RuntimeError("Tokenizer must be fitted using `.fit(text)` before decoding.")
            
        if not token_ids:
            return ""

        decoded_chars = []
        for token_id in token_ids:
            if token_id not in self.id_to_char:
                raise ValueError(f"Invalid token ID encountered: {token_id}. Not present in vocabulary.")
            decoded_chars.append(self.id_to_char[token_id])
            
        return "".join(decoded_chars)

    @property
    def vocab_size(self) -> int:
        """Returns the total size of the vocabulary."""
        return len(self.chars)


# --- Local Verification Script ---
if __name__ == "__main__":
    print("=== Character Tokenizer Diagnostics ===")
    
    # Instantiates with default visible "?" token
    tokenizer = CharTokenizer()
    
    # 1. Validation Check: Encode before fit
    try:
        tokenizer.encode("hello")
    except RuntimeError as e:
        print(f"✔ Encode before fit validation caught: {e}")

    # 2. Validation Check: Fit and test basic conceptual example
    sample_corpus = "hello world"
    tokenizer.fit(sample_corpus)
    print(f"✔ Tokenizer fitted successfully. Vocab Size: {tokenizer.vocab_size}")
    print(f"Vocabulary Mapping: {tokenizer.char_to_id}")

    # 3. Validation Check: Empty text handling
    assert tokenizer.encode("") == []
    assert tokenizer.decode([]) == ""
    print("✔ Empty text and empty list validations passed.")

    # 4. Validation Check: Unknown character handling
    # 'x' and 'z' are not in "hello world", so they will map to the "?" character token ID
    encoded = tokenizer.encode("hexzlo")
    print(f"Encoded string 'hexzlo' -> {encoded}")
    decoded = tokenizer.decode(encoded)
    print(f"Decoded string back      -> '{decoded}'")

    # 5. Validation Check: Decode invalid token ID
    try:
        tokenizer.decode([999])
    except ValueError as e:
        print(f"✔ Decode invalid token ID validation caught: {e}")
