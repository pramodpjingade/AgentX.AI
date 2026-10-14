from typing import List, Dict, Any, Optional
from loguru import logger

class FailoverManager:
    """
    Failover Manager & Circuit Breaker for AgentX.
    Manages automatic retries, model switching, and provider fallback transitions.
    Ensures missions never crash due to provider downtime.
    """

    PROVIDER_FALLBACK_CHAIN = {
        "openai": ["anthropic", "google", "ollama", "mock"],
        "anthropic": ["openai", "google", "ollama", "mock"],
        "google": ["openai", "anthropic", "ollama", "mock"],
        "ollama": ["mock"],
        "mock": []
    }

    def __init__(self):
        # Provider (str) -> failure count (int)
        self._circuit_breakers: Dict[str, int] = {}
        logger.info("FailoverManager: Provider Failover Manager initialized.")

    def record_failure(self, provider: str):
        """Records a provider failure event."""
        self._circuit_breakers[provider] = self._circuit_breakers.get(provider, 0) + 1
        logger.warning(f"FailoverManager: Provider '{provider}' recorded failure (Count: {self._circuit_breakers[provider]})")

    def record_success(self, provider: str):
        """Resets circuit breaker for provider on success."""
        if provider in self._circuit_breakers:
            self._circuit_breakers[provider] = 0

    def get_fallback_provider(self, primary_provider: str) -> str:
        """Returns the next healthy fallback provider in the failover chain."""
        chain = self.PROVIDER_FALLBACK_CHAIN.get(primary_provider.lower(), ["mock"])
        for fallback in chain:
            failures = self._circuit_breakers.get(fallback, 0)
            if failures < 3:
                logger.info(f"FailoverManager: Switching from '{primary_provider}' to fallback provider '{fallback}'")
                return fallback
        return "mock"
