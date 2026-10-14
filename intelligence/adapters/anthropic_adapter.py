import os
import time
from typing import Optional, Dict, Any
from loguru import logger

from intelligence.base_adapter import BaseProviderAdapter
from intelligence.response_object import ModelResponse
from intelligence.cost_optimizer import CostOptimizer

class AnthropicAdapter(BaseProviderAdapter):
    """Anthropic Claude Model Provider Adapter for AgentX."""

    def __init__(self):
        super().__init__("anthropic")
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def is_configured(self) -> bool:
        key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
        return bool(key and "your-" not in key and len(key.strip()) > 5)

    async def execute(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> ModelResponse:
        start_time = time.time()
        key = os.getenv("ANTHROPIC_API_KEY") or self.api_key
        model = model_name or os.getenv("DEFAULT_ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")

        if not self.is_configured():
            return ModelResponse(
                response_text=(
                    "⚠️ **Anthropic Claude API Key Not Configured**\n\n"
                    "Please provide a valid `ANTHROPIC_API_KEY` in your `.env` file to enable Claude models."
                ),
                provider="anthropic",
                model=model,
                confidence_score=0.0,
                finish_reason="error",
                safety_flags=["MISSING_CREDENTIALS: ANTHROPIC_API_KEY"]
            )

        try:
            from langchain_anthropic import ChatAnthropic
            client = ChatAnthropic(
                model=model,
                anthropic_api_key=key,
                temperature=temperature,
                max_tokens_to_sample=max_tokens,
                default_request_timeout=45.0,
                max_retries=2
            )
            messages = [("system", system_instruction), ("human", prompt)]
            res = await client.ainvoke(messages)
            response_text = str(res.content)

            latency_ms = int((time.time() - start_time) * 1000)
            prompt_tokens = len(prompt) // 4
            completion_tokens = len(response_text) // 4
            total_tokens = prompt_tokens + completion_tokens
            cost = CostOptimizer.calculate_cost(model, prompt_tokens, completion_tokens)

            return ModelResponse(
                response_text=response_text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                cost_usd=cost,
                provider="anthropic",
                model=model,
                confidence_score=0.98,
                finish_reason="stop"
            )
        except Exception as e:
            logger.error(f"AnthropicAdapter execution error: {e}")
            latency_ms = int((time.time() - start_time) * 1000)
            return ModelResponse(
                response_text=f"[Model Provider Error (anthropic)] {str(e)}",
                latency_ms=latency_ms,
                provider="anthropic",
                model=model,
                confidence_score=0.0,
                finish_reason="error",
                safety_flags=[f"ProviderError: {e}"]
            )

    async def stream(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        key = os.getenv("ANTHROPIC_API_KEY") or self.api_key
        model = model_name or os.getenv("DEFAULT_ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")

        if not self.is_configured():
            yield (
                "**[AgentX Configuration Required]**\n\n"
                "Please configure a valid `ANTHROPIC_API_KEY` in your `.env` file to enable Claude models."
            )
            return

        try:
            from langchain_anthropic import ChatAnthropic
            client = ChatAnthropic(
                model=model,
                anthropic_api_key=key,
                temperature=temperature,
                max_tokens_to_sample=max_tokens,
                default_request_timeout=45.0,
                max_retries=2
            )
            messages = [("system", system_instruction), ("human", prompt)]
            async for chunk in client.astream(messages):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as e:
            logger.error(f"AnthropicAdapter streaming error: {e}")
            yield f"[Model Provider Error (anthropic)] {str(e)}"
