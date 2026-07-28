import re
from pathlib import Path
from typing import Dict, List, Union

class SpecialTokenizer:
    def __init__(self):
        self.token_to_id = {"<PAD>": 0, "<UNK>": 1, "<BOS>": 2, "<EOS>": 3}
        self.id_to_token = {0: "<PAD>", 1: "<UNK>", 2: "<BOS>", 3: "<EOS>"}

    def _tokenize(self, text:str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def build_vocab_from_file(self, file_path: Union[str, Path]):
        text = Path(file_path).read_text(encoding="utf-8")
        tokens = self._tokenize(text)

        unique_tokens = sorted(list(set(tokens)))

        current_id = 4
        for token in unique_tokens:
            if token not in self.token_to_id:
                self.token_to_id[token] = current_id
                self.id_to_token[current_id] = token
                current_id += 1

    def encode(self, text: str) -> List[int]:
        words = self._tokenize(text)
        encoded_ids = [self.token_to_id["<BOS>"]]
        for word in words:
            encoded_ids.append(self.token_to_id.get(word, 1))
        encoded_ids.append(self.token_to_id["<EOS>"])
        return encoded_ids

    def decoded(self, ids:List[int], strip_special: bool = True) -> str:
        tokens = []
        for token_id in ids:
            token_str = self.id_to_token.get(token_id, "<UNK>")

            if strip_special and token_str in ["<PAD>", "<BOS>", "<EOS>"]:
                continue

            tokens.append(token_str)

        return " ".join(tokens)

if __name__ == "__main__":

        tokenizer = SpecialTokenizer()
        tokenizer.build_vocab_from_file("dataset.txt")

        original_Sentence = "Retail banking platforms require authentication."


        print("\n--- Starting Round-Trip Validation Test ---")
        print(f"1. Original Input:   {original_Sentence}")

        encoded_sequence = tokenizer.encode(original_Sentence)  
        print(f":Encoded token ids: {encoded_sequence}")

        decoded_sentence = tokenizer.decoded(encoded_sequence)
        print(f"Decoded Opution: {decoded_sentence}")

        clean_original = " ".join(tokenizer._tokenize(original_Sentence))

        print("-" * 44)
        if clean_original == decoded_sentence:
            print("✅ SUCCESS: Round-trip loop matches perfectly!")
        else:
            print("❌ FAILURE: Mismatch found between encoder and decoder.")