from collections.abc import Iterator
import json

from pydantic import BaseModel

import requests

from .streaming import StreamChunk
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

    def _build_options(self, request: GenerationRequest) -> dict:
        options = {
            "temperature": request.temperature,
            "num_predict": request.max_tokens,
        }

        if getattr(request, "top_p", None) is not None:
            options["top_p"] = request.top_p

        if getattr(request, "seed", None) is not None:
            options["seed"] = request.seed

        return options

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
                "options": self._build_options(request),
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

    def generate_stream(
        self,
        request: GenerationRequest,
    ) -> Iterator[StreamChunk]:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": request.model,
                "prompt": request.prompt,
                "stream": True,
                "options": self._build_options(request),
            },
            stream=True,
            timeout=self.timeout,
        )

        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            data = json.loads(line)

            yield StreamChunk(
                text=data.get("response", ""),
                done=data.get("done", False),
            )

    def generate_structured(
        self,
        request: GenerationRequest,
        response_model: type[BaseModel],
    ) -> BaseModel:

        schema = response_model.model_json_schema()

        structured_prompt = f"""
        Return your response as valid JSON.

        The response must conform to this schema:

        {json.dumps(schema, indent=2)}

        User request:

        {request.prompt}
        """

        structured_request = GenerationRequest(
            prompt=structured_prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            seed=request.seed,
        )

        response = self.generate(structured_request)

        return response_model.model_validate_json(response.text)

    def health_check(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            return response.status_code == 200

        except requests.RequestException:
            return False
