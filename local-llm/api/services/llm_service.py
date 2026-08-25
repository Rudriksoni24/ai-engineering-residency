class LLMService:

    def __init__(self, runtime):
        self.runtime = runtime

    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
    ):
        from runtime.runtime_types import GenerationRequest

        request = GenerationRequest(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return self.runtime.generate(request)