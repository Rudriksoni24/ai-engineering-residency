import requests

from .base import LLMRuntime
from .runtime_types import (
    GenerationRequest,
    GenerationResponse,
)


class OllamaRuntime(LLMRuntime):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": request.model,
                "prompt": request.prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens,
                },
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        return GenerationResponse(
            text=data["response"],
            model=data["model"],
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
            metadata={
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
                "eval_duration": data.get("eval_duration"),
            },
        )

    def health_check(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            return response.status_code == 200

        except requests.RequestException:
            return False