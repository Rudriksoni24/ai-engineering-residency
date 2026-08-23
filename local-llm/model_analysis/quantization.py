from dataclasses import dataclass


@dataclass(frozen=True)
class QuantizationProfile:
    name: str
    bits_per_parameter: float
    description: str


FP32 = QuantizationProfile(
    name="FP32",
    bits_per_parameter=32,
    description="Full precision floating point.",
)

FP16 = QuantizationProfile(
    name="FP16",
    bits_per_parameter=16,
    description="Half precision floating point.",
)

INT8 = QuantizationProfile(
    name="INT8",
    bits_per_parameter=8,
    description="Eight-bit quantized representation.",
)

Q4 = QuantizationProfile(
    name="Q4",
    bits_per_parameter=4,
    description="Approximate four-bit quantized representation.",
)