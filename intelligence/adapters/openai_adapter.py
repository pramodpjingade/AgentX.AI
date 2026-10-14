import os
import time
from typing import Optional, Dict, Any
from loguru import logger

from intelligence.base_adapter import BaseProviderAdapter
from intelligence.response_object import ModelResponse
from intelligence.cost_optimizer import CostOptimizer

class OpenAIAdapter(BaseProviderAdapter):
    """OpenAI Model Provider Adapter for AgentX."""

    def __init__(self):
        super().__init__("openai")
        self.api_key = os.getenv("OPENAI_API_KEY")

    def is_configured(self) -> bool:
        key = self.api_key or os.getenv("OPENAI_API_KEY")
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
        key = os.getenv("OPENAI_API_KEY") or self.api_key
        model = model_name or os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")

        if not self.is_configured():
            return ModelResponse(
                response_text=(
                    "⚠️ **OpenAI API Key Not Configured**\n\n"
                    "Please provide a valid `OPENAI_API_KEY` in your `.env` file to enable OpenAI models."
                ),
                provider="openai",
                model=model,
                confidence_score=0.0,
                finish_reason="error",
                safety_flags=["MISSING_CREDENTIALS: OPENAI_API_KEY"]
            )

        try:
            from langchain_openai import ChatOpenAI
            client = ChatOpenAI(
                model=model,
                openai_api_key=key,
                temperature=temperature,
                max_tokens=max_tokens,
                request_timeout=45.0,
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
                provider="openai",
                model=model,
                confidence_score=0.98,
                finish_reason="stop"
            )
        except Exception as e:
            logger.error(f"OpenAIAdapter execution error: {e}")
            latency_ms = int((time.time() - start_time) * 1000)
            return ModelResponse(
                response_text=f"[Model Provider Error (openai)] {str(e)}",
                latency_ms=latency_ms,
                provider="openai",
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
        key = os.getenv("OPENAI_API_KEY") or self.api_key
        model = model_name or os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")

        if not self.is_configured():
            yield (
                "**[AgentX Configuration Required]**\n\n"
                "Please configure a valid `OPENAI_API_KEY` in your `.env` file to enable OpenAI models."
            )
            return

        try:
            from langchain_openai import ChatOpenAI
            client = ChatOpenAI(
                model=model,
                openai_api_key=key,
                temperature=temperature,
                max_tokens=max_tokens,
                request_timeout=45.0,
                max_retries=2
            )
            messages = [("system", system_instruction), ("human", prompt)]
            async for chunk in client.astream(messages):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as e:
            logger.error(f"OpenAIAdapter streaming error: {e}")
            yield f"[Model Provider Error (openai)] {str(e)}"
