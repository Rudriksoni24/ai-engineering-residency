from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    prompt: str
    expected_keywords: tuple[str, ...] = ()
    expects_json: bool = False


@dataclass
class BenchmarkResult:
    case_name: str
    model: str
    runtime: str
    latency_seconds: float
    output: str
    keyword_score: Optional[float] = None
    valid_json: Optional[bool] = None