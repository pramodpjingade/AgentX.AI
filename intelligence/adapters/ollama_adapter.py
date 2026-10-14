import os
import time
import httpx
from typing import Optional, Dict, Any
from loguru import logger

from intelligence.base_adapter import BaseProviderAdapter
from intelligence.response_object import ModelResponse
from intelligence.cost_optimizer import CostOptimizer

class OllamaAdapter(BaseProviderAdapter):
    """Local Ollama Model Provider Adapter for AgentX."""

    def __init__(self):
        super().__init__("ollama")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")

    def is_configured(self) -> bool:
        # Check if explicitly enabled or if OLLAMA_ENABLED is true
        explicit = os.getenv("OLLAMA_ENABLED", "").lower() in ["1", "true", "yes"]
        return explicit

    async def execute(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> ModelResponse:
        start_time = time.time()
        base_url = os.getenv("OLLAMA_BASE_URL", self.base_url).rstrip("/")
        model = model_name or os.getenv("DEFAULT_OLLAMA_MODEL", "llama3")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                res = await client.post(f"{base_url}/api/chat", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("message", {}).get("content", "")
                    prompt_tokens = data.get("prompt_eval_count", len(prompt) // 4)
                    completion_tokens = data.get("eval_count", len(response_text) // 4)
                    total_tokens = prompt_tokens + completion_tokens
                    latency_ms = int((time.time() - start_time) * 1000)

                    return ModelResponse(
                        response_text=response_text,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        latency_ms=latency_ms,
                        cost_usd=0.0,
                        provider="ollama",
                        model=model,
                        confidence_score=0.95,
                        finish_reason="stop"
                    )
                else:
                    raise RuntimeError(f"Ollama returned HTTP {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"OllamaAdapter execution error: {e}")
            latency_ms = int((time.time() - start_time) * 1000)
            return ModelResponse(
                response_text=(
                    f"[Local Ollama Model Error] Could not reach local Ollama at '{base_url}'.\n"
                    f"Please ensure Ollama is installed and running ('ollama serve'), or configure a cloud provider."
                ),
                latency_ms=latency_ms,
                provider="ollama",
                model=model,
                confidence_score=0.0,
                finish_reason="error",
                safety_flags=[f"OllamaError: {e}"]
            )

    async def stream(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        base_url = os.getenv("OLLAMA_BASE_URL", self.base_url).rstrip("/")
        model = model_name or os.getenv("DEFAULT_OLLAMA_MODEL", "llama3")

        try:
            import json
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                async with client.stream("POST", f"{base_url}/api/chat", json=payload) as res:
                    if res.status_code != 200:
                        yield f"[Local Ollama Error] HTTP {res.status_code}"
                        return
                    async for line in res.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                content = data.get("message", {}).get("content", "")
                                if content:
                                    yield content
                            except Exception:
                                pass
        except Exception as e:
            logger.error(f"OllamaAdapter streaming error: {e}")
            yield f"[Local Ollama Model Error] {str(e)}"
