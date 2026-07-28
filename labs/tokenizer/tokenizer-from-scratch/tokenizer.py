import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Union

class SimpleTokenizer:
    def __init__(self):
        self.token_to_id = {"[PAD]": 0, "[UNK]": 1}
        self.id_to_token = {0: "[PAD]", 1: "[UNK]"}
        self.frequencies = {"[PAD]": 0, "[UNK]": 0}

    def _tokenize(self, text:str) -> List[str]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        return tokens

    def build_vocab(self, text_or_path: Union[str, Path], min_freq: int = 1):
        if isinstance(text_or_path, Path) or isinstance(text_or_path, str) and Path(text_or_path).is_file():
            text = Path(text_or_path).read_text(encoding="utf-8")
        else:
            text = str(text_or_path)

        tokens = self._tokenize(text)
        counts = Counter(tokens)

        sorted_tokens = sorted(
            [item for item in counts.items() if item[1] >= min_freq],
            key = lambda x: (-x[1], x[0]),
        )

        self.token_to_id = {"[PAD]": 0, "[UNK]": 1}
        self.id_to_token = {0: "[PAD]", 1: "[UNK]"}
        self.frequencies = {"[PAD]": 0, "[UNK]": 0}

        for current_id, (token, freq) in enumerate(sorted_tokens, start=2):
            self.token_to_id[token] = current_id
            self.id_to_token[current_id] = token
            self.frequencies[token] = freq

    def encode(self, text: str) -> list:
        tokens = self._tokenize(text)
        return [self.token_to_id.get(token, 1) for token in tokens]

    def decode(self, ids: List[int]) -> str:
        tokens = [self.id_to_token.get(token_id, "[UNK]") for token_id in ids]
        return " ".join(tokens)

    def save(self, file_path:Union[str, Path]):
        data = {
            "token_to_id": self.token_to_id,
            "id_to_token": {str(k): v for k, v in self.id_to_token.items()},
            "frequencies": self.frequencies,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Vocabulary saved to {file_path}")

    def load(self, file_path:Union[str, Path]):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.token_to_id = data["token_to_id"]
        self.id_to_token = {int(k): v for k, v in data["id_to_token"].items()}
        self.frequencies = data["frequencies"]
        print(f"Tokenizer state loaded from {file_path}")

if __name__ == "__main__":
    sample_corpus = (
        "Apple is a fruit. Orange is a fruit. BMW makes cars. Tesla builds EVs."
    )
    tokenizer = SimpleTokenizer()
    tokenizer.build_vocab(sample_corpus)

    print(f"Vocab size: {len(tokenizer.token_to_id)} unique tokens.")

    test_phrase = "Tesla builds an electric car!"
    encoded_ids = tokenizer.encode(test_phrase)
    print(f"Encoded IDs for '{test_phrase}': {encoded_ids}")

    decoded_text = tokenizer.decode(encoded_ids)
    print(f"Decoded text from IDs: '{decoded_text}'")

    Json_Path = "tokenizer_config.json"
    tokenizer.save(Json_Path)

    new_tokenizer = SimpleTokenizer()
    new_tokenizer.load(Json_Path)

    assert (
        new_tokenizer.encode(test_phrase) == encoded_ids
    ), "Encoding mismatch after loading config!"
    print("\n Verification successful! save/load cycle works correctly.")
