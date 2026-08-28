from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProfile:
    """Immutable profile holding core high-level metadata for a local language model.
    
    Intentionally simplified for high-level tracking. Extended hardware metrics 
    such as layers and attention dimensions will be integrated later for exact 
    KV cache calculations.
    """
    name: str
    parameters_billion: float
    context_window: int
    quantization: str
    bits_per_parameter: float
