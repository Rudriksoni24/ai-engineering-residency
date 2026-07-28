import json
import re
from collections import Counter
from pathlib import Path

def build_vocabulary(dataset_path: str, output_json_path: str, min_freq: int = 1):
    path = Path(dataset_path)
    if not path.exists():
        sample_text = (
            "Apple is a fruit.\nOrange is a fruit.\nBMW makes cars.\n"
            "Tesla builds EVs.\nPython is a language.\nSwift is a language."
        )
        path.write_text(sample_text, encoding="utf-8")
        print(f"Sample dataset created at {dataset_path}")

    text = path.read_text(encoding="utf-8")
    tokens = re.findall(r"\b\w+\b", text.lower())

    token_counts = Counter(tokens)

    filtered_tokens = {
        token: count
        for token, count in token_counts.items()
        if count >= min_freq
    }

    sorted_tokens = sorted(
        filtered_tokens.items(), key=lambda x:(-x[1], x[0])
    )

    vocabulary = {
        "token_to_id": {"[PAD]": 0, "[UNK]": 1},
        "id_to_token": {"0": "[PAD]", "1": "[UNK]"},
        "frequencies": {"[PAD]": 0, "[UNK]": 0},
    }

    current_id = 2
    for token, freq in sorted_tokens:
        vocabulary["token_to_id"][token] = current_id
        vocabulary["id_to_token"][str(current_id)] = token
        vocabulary["frequencies"][token] = freq
        current_id += 1

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(vocabulary, f, indent=4, ensure_ascii=False)

    print(f"Vocabulary built and saved to {output_json_path}")
    print(f"Total unique tokens: {len(sorted_tokens)}")
    print("\n Top 5 Most Frequent Tokens:")
    for token, freq in sorted_tokens[:5]:
        print(f" '{token}' : {freq} occurrences")

if __name__ == "__main__":
    dataset_path = "dataset.txt"
    output_json_path = "vocabulary.json"

    build_vocabulary(dataset_path, output_json_path)
