import httpx


class OllamaAgentGenerator:

    def __init__(
        self,
        model: str,
        base_url: str = (
            "http://localhost:11434"
        ),
        timeout: float = 120.0,
    ) -> None:

        if not model.strip():
            raise ValueError(
                "model cannot be empty"
            )

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
    ) -> str:

        if not prompt.strip():
            raise ValueError(
                "prompt cannot be empty"
            )

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        result = payload.get(
            "response",
            ""
        ).strip()

        if not result:
            raise RuntimeError(
                "Ollama returned an empty response"
            )

        return result