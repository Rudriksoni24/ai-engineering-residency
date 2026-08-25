from dataclasses import dataclass

from api.services.llm_service import LLMService


@dataclass
class FakeResponse:
    text: str
    model: str


class FakeRuntime:

    def generate(self, request):
        return FakeResponse(
            text="fake response",
            model=request.model,
        )


def test_llm_service_generate():
    service = LLMService(
        runtime=FakeRuntime(),
    )

    response = service.generate(
        prompt="Hello",
        model="test-model",
        max_tokens=10,
        temperature=0,
    )

    assert response.text == "fake response"
    assert response.model == "test-model"