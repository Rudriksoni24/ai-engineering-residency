from local_llm.runtime.streaming import StreamChunk

# Then test the Ollama implementation using mocks.

# Do not require a real model for every test.

def test_stream_chunk_defaults():
    chunk = StreamChunk(
        text="Hello",
    )

    assert chunk.text == "Hello"
    assert chunk.done is False


def test_stream_chunk_completion():
    chunk = StreamChunk(
        text="",
        done=True,
    )

    assert chunk.done is True