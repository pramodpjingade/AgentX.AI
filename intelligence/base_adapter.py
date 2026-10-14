from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from intelligence.response_object import ModelResponse

class BaseProviderAdapter(ABC):
    """
    Abstract Base Provider Adapter for AgentX (Phase 5 Intelligence Layer).
    Normalizes provider communication, execution, streaming, and metric logging.
    """

    def __init__(self, provider_name: str):
        self.provider_name = provider_name.lower()

    @abstractmethod
    def is_configured(self) -> bool:
        """Checks if provider credentials/keys are properly configured."""
        pass

    @abstractmethod
    async def execute(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> ModelResponse:
        """
        Executes model prompt request and returns a normalized ModelResponse object.
        """
        pass
