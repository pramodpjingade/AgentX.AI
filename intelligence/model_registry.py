from typing import Dict, Any, List, Optional
from loguru import logger

class ModelRegistry:
    """
    Model Registry for AgentX (Phase 5 Intelligence Router).
    Indexes model specs, context limits, pricing matrices, capability scores, and provider mappings.
    """

    DEFAULT_PRICING = {
        "gpt-4o": {"input_per_m": 5.00, "output_per_m": 15.00},
        "gpt-4o-mini": {"input_per_m": 0.15, "output_per_m": 0.60},
        "claude-3-5-sonnet-20240620": {"input_per_m": 3.00, "output_per_m": 15.00},
        "gemini-1.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
        "gemini-1.5-pro": {"input_per_m": 1.25, "output_per_m": 5.00},
        "deepseek-chat": {"input_per_m": 0.14, "output_per_m": 0.28},
        "llama3": {"input_per_m": 0.0, "output_per_m": 0.0},
        "mock": {"input_per_m": 0.0, "output_per_m": 0.0}
    }

    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._register_default_models()
        logger.info("ModelRegistry: Model Intelligence Registry initialized.")

    def register_model(
        self,
        model_name: str,
        provider: str,
        version: str = "1.0",
        capabilities: Optional[List[str]] = None,
        context_window: int = 128000,
        reasoning_score: float = 0.85,
        coding_score: float = 0.85,
        pricing: Optional[Dict[str, float]] = None,
        tier: str = "fast"  # fast, reasoning, coding, vision, local
    ):
        """Registers a model spec descriptor into the registry."""
        self._registry[model_name] = {
            "model_name": model_name,
            "provider": provider,
            "version": version,
            "capabilities": capabilities or ["text_generation"],
            "context_window": context_window,
            "reasoning_score": reasoning_score,
            "coding_score": coding_score,
            "pricing": pricing or self.DEFAULT_PRICING.get(model_name, {"input_per_m": 0.0, "output_per_m": 0.0}),
            "tier": tier,
            "health_status": "HEALTHY"
        }

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves spec descriptor for a registered model."""
        return self._registry.get(model_name)

    def find_best_model_for_task(self, task_type: str, preferred_provider: Optional[str] = None) -> Dict[str, Any]:
        """Selects optimal model spec based on task type requirements."""
        tier_map = {
            "coding": "coding",
            "reasoning": "reasoning",
            "planning": "reasoning",
            "vision": "vision",
            "rag": "fast",
            "general": "fast"
        }
        target_tier = tier_map.get(task_type.lower(), "fast")

        candidates = [m for m in self._registry.values() if m["tier"] == target_tier]
        if preferred_provider:
            pref_candidates = [m for m in candidates if m["provider"].lower() == preferred_provider.lower()]
            if pref_candidates:
                return pref_candidates[0]

        if candidates:
            return candidates[0]

        return self._registry.get("gpt-4o-mini", list(self._registry.values())[0])

    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """Lists all registered models."""
        return self._registry

    def _register_default_models(self):
        """Pre-registers default model definitions."""
        self.register_model("gpt-4o-mini", "openai", capabilities=["text", "json", "tools"], reasoning_score=0.82, tier="fast")
        self.register_model("gpt-4o", "openai", capabilities=["text", "json", "tools", "vision"], reasoning_score=0.96, tier="reasoning")
        self.register_model("claude-3-5-sonnet-20240620", "anthropic", capabilities=["text", "json", "coding"], coding_score=0.98, tier="coding")
        self.register_model("gemini-1.5-flash", "google", capabilities=["text", "vision", "multimodal"], tier="vision")
        self.register_model("llama3", "ollama", capabilities=["text", "local"], tier="local")
        self.register_model("mock-model", "mock", capabilities=["text", "testing"], tier="fast")
