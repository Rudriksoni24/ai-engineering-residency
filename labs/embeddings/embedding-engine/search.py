import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

# 1. Resolve path to your embedding lab dynamically
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from embedding import RandomEmbeddingLookup

def generate_embedding_space_plot():
    # 1. Force the file lookup path directly inside the directory where you are currently working
    # Check current directory first, then fallback to relative locations
    if Path("dataset.txt").exists():
        dataset_file = Path("dataset.txt").resolve()
    else:
        LABS_ROOT = CURRENT_DIR.parent.parent
        dataset_file = (LABS_ROOT / "tokenizer" / "tokenizer-from-scratch" / "dataset.txt").resolve()

    print(f"📖 Reading dataset live from: {dataset_file}")
    
    # Debug print: Show the very last line of the file to confirm your edits are visible here
    lines = dataset_file.read_text(encoding="utf-8").strip().splitlines()
    print(f"📄 Total lines found in file: {len(lines)}")
    print(f"📝 Last line content: '{lines[-1]}'")

    # 2. Initialize the lookup system using this exact file
    system = RandomEmbeddingLookup(dataset_path=dataset_file, embedding_dim=64)
    
    # 3. Define target words to isolate and plot
    target_words = ["bank", "money", "finance", "loan", "apple", "orange", "swift", "python", "kubernetes", "kafka"]
    
    # Print out a slice of the vocabulary keys for debugging
    vocab_keys = list(system.tokenizer.token_to_id.keys())
    print(f"🔍 First 15 vocabulary keys registered: {vocab_keys[:15]}")
    
    vectors = []
    valid_labels = []
    
    for word in target_words:
        # Check against vocabulary directly
        if word in system.tokenizer.token_to_id:
            vector_tensor = system.lookup_word(word)
            vectors.append(vector_tensor.numpy())
            valid_labels.append(word)
        else:
            print(f"⚠️ Word '{word}' missing from vocabulary mapping, skipping plot tracking.")

    if len(vectors) < 2:
        print("❌ Error: Not enough valid words found to project a 2D space.")
        return

    vectors_array = np.array(vectors)

    # 4. Apply PCA Dimensionality Reduction
    pca = PCA(n_components=2, random_state=42)
    vectors_2d = pca.fit_transform(vectors_array)

    # 5. Construct and style the Matplotlib Scatter Plot
    plt.figure(figsize=(10, 8), dpi=150)
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
    plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)
    plt.scatter(vectors_2d[:, 0], vectors_2d[:, 1], color='#4A90E2', s=120, edgecolors='black', zorder=3)

    for i, label in enumerate(valid_labels):
        plt.text(vectors_2d[i, 0] + 0.05, vectors_2d[i, 1] + 0.05, label, fontsize=12, weight='bold', zorder=4)

    plt.title("2D Projection of Vector Space via PCA", fontsize=14, pad=15, weight='bold')
    plt.grid(True, linestyle=':', alpha=0.6)
    
    output_filename = "embedding-space.png"
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close()
    
    print(f"\n🎨 Visual map successfully exported and saved as: {output_filename}")

if __name__ == "__main__":
    generate_embedding_space_plot()
