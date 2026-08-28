from .model_profile import ModelProfile


BYTES_PER_GIB = 1024**3


def estimate_weight_memory_gib(
    model: ModelProfile,
) -> float:
    """
    Estimate memory required for model weights.

    This is an approximation and does not include runtime overhead,
    KV cache, temporary buffers, or operating system memory.
    """

    parameters = model.parameters_billion * 1_000_000_000

    total_bits = parameters * model.bits_per_parameter

    total_bytes = total_bits / 8

    return total_bytes / BYTES_PER_GIB

def estimate_memory_from_parameters(
    parameters_billion: float,
    bits_per_parameter: float,
) -> float:
    parameters = parameters_billion * 1_000_000_000
    total_bits = parameters * bits_per_parameter
    total_bytes = total_bits / 8

    return total_bytes / BYTES_PER_GIB

# Programmatic implementation of the profiles
# small_model = ModelProfile(
#     name="3B-Q4",
#     parameters_billion=3.0,
#     context_window=8192,
#     quantization="Q4",
#     bits_per_parameter=4.0,
# )

# medium_model = ModelProfile(
#     name="8B-Q4",
#     parameters_billion=8.0,
#     context_window=8192,
#     quantization="Q4",
#     bits_per_parameter=4.0,
# )

# large_model = ModelProfile(
#     name="14B-Q4",
#     parameters_billion=14.0,
#     context_window=8192,
#     quantization="Q4",
#     bits_per_parameter=4.0,
# )
