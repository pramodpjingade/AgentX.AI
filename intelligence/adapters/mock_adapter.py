import time
import asyncio
from typing import Optional, Dict, Any
from loguru import logger

from intelligence.base_adapter import BaseProviderAdapter
from intelligence.response_object import ModelResponse
from intelligence.cost_optimizer import CostOptimizer

class MockAdapter(BaseProviderAdapter):
    """Mock Provider Adapter for offline local testing and fallback execution."""

    def __init__(self):
        super().__init__("mock")

    def is_configured(self) -> bool:
        return True

    async def execute(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> ModelResponse:
        start_time = time.time()
        model_used = model_name or "mock-model"
        await asyncio.sleep(0.1)  # Simulate 100ms LLM processing latency

        # Generate dynamic diagnostic text based on prompt
        from agents.model_manager import ModelManager
        mm = ModelManager()
        response_text = mm._generate_mock_response(prompt, system_instruction)

        execution_time = time.time() - start_time
        latency_ms = int(execution_time * 1000)

        prompt_tokens = len(prompt) // 4
        completion_tokens = len(response_text) // 4
        total_tokens = prompt_tokens + completion_tokens
        cost_usd = CostOptimizer.calculate_cost("mock", prompt_tokens, completion_tokens)

        return ModelResponse(
            response_text=response_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            provider="mock",
            model=model_used,
            confidence_score=0.98,
            finish_reason="stop"
        )
