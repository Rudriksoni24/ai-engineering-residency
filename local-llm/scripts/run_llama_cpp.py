import subprocess
from pathlib import Path

# Updated to match your exact local filename on your Mac M2
MODEL_PATH = Path.home() / "ai-models/gguf/Qwen3-4B-Q4_K_M.gguf"


def generate(
    prompt: str,
    max_tokens: int = 256,
) -> str:
    command = [
        "llama-cli",
        "-m",
        str(MODEL_PATH),
        "-p",
        prompt,
        "-n",
        str(max_tokens),
        "--log-disable",  # Suppresses internal engine logging to isolate pure stdout
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error during llama-cli execution:\n{e.stderr}")
        raise


if __name__ == "__main__":
    print("--- Starting CLI Subprocess Harness Run ---")
    response = generate(
        "Explain the difference between an LLM model and an LLM runtime."
    )
    print(response)
