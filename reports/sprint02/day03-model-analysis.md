# Sprint 2 Day 3 — Local Model Analysis

## Hardware

- Machine: Apple Silicon M2
- Unified Memory: 16 GB
- Primary Use: Local AI/ML development

## Memory Formula

Approximate weight memory:

parameters × bits_per_parameter / 8

This does not include:

- KV cache
- Runtime overhead
- Temporary buffers
- Operating system memory
- Other running applications

## Model Profiles

| Model | Parameters | Quantization | Approx Weight Memory | Context |
| :--- | ---: | :--- | ---: | ---: |
| **Small** | 3B | Q4 | **~1.4 GiB** | 8192 |
| **Medium** | 8B | Q4 | **~3.7 GiB** | 8192 |
| **Large** | 14B | Q4 | **~6.5 GiB** | 8192 |

*Note: Calculations leverage exact binary conversion thresholds ($1\text{ GiB} = 2^{30}\text{ bytes}$).*

## Initial Conclusion

### Which model sizes are practical?
The **Small (3B)** and **Medium (8B)** models are highly practical on this machine. An 8B model quantised to Q4 consumes roughly 3.7 GiB of weight memory, which easily slides under macOS's default memory limits while leaving substantial room for the operating system, IDEs, local servers, and browsers. Because Apple Silicon uses a unified memory architecture, the GPU can access these weights at full memory bus speeds without forcing data copies across distinct VRAM segments.

### Which model sizes are possible but likely inconvenient?
The **Large (14B)** model is theoretically possible to load but will be operationally inconvenient. At 6.5 GiB for the raw parameters alone, the baseline space requirements double. Once a standard context window (e.g., 8k tokens) scales up, the dynamic memory consumption of the KV cache along with runtime buffer allocations will rapidly approach 10–12 GiB. This forces heavy memory compression, forces browser tabs to swap out to disk, and risks triggering system lag or sudden engine termination via Out-Of-Memory (OOM) routine sweeps.

### Which workloads would require a larger machine or remote/on-prem server?
Any assignments demanding **unquantized base architectures (FP16/FP32)**, models scaling past **32B+ parameters**, or intensive **multi-user concurrent serving pipelines** will require a larger workstation (e.g., a 64 GB/128 GB Studio variant) or an off-system cloud compute instance. Additionally, deep context extension runs (e.g., 32k to 128k context windows) swell the KV cache to a scale where a 16 GB system memory pool is exhausted before inference processing even gets underway.
