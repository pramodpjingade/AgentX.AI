from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ModelResponse:
    """
    Standardized Model Response Payload across all LLM Providers in AgentX (Phase 5 Intelligence Layer).
    Normalizes text outputs, structured JSON, tool calls, token usage, costs, latencies, and safety flags.
    """
    response_text: str = ""
    structured_json: Optional[Dict[str, Any]] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    provider: str = "mock"
    model: str = "mock-model"
    confidence_score: float = 1.0
    finish_reason: str = "stop"  # stop, length, tool_calls, error
    safety_flags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes ModelResponse into a clean dictionary."""
        return {
            "response_text": self.response_text,
            "structured_json": self.structured_json,
            "tool_calls": self.tool_calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "provider": self.provider,
            "model": self.model,
            "confidence_score": self.confidence_score,
            "finish_reason": self.finish_reason,
            "safety_flags": self.safety_flags,
            "metadata": self.metadata
        }
