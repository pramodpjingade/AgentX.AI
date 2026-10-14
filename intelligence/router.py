import time
import uuid
from typing import Dict, Any, Optional
from loguru import logger

from intelligence.response_object import ModelResponse
from intelligence.model_registry import ModelRegistry
from intelligence.task_classifier import TaskClassifier
from intelligence.cost_optimizer import CostOptimizer
from intelligence.prompt_optimizer import PromptOptimizer
from intelligence.safety_layer import SafetyLayer
from intelligence.failover import FailoverManager
from intelligence.response_validator import ResponseValidator
from intelligence.adapters.mock_adapter import MockAdapter
from intelligence.adapters.openai_adapter import OpenAIAdapter
from database.connection import async_session
from database.models import ModelRouterLog

class IntelligenceRouter:
    """
    Central Multi-Model Intelligence Router for AgentX (Phase 5 AI Gateway).
    Decouples AI agents from LLM providers, automatically selects optimal models,
    optimizes prompts, manages costs, handles retries/failover, and normalizes ModelResponse output objects.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IntelligenceRouter, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.registry = ModelRegistry()
        self.task_classifier = TaskClassifier()
        self.prompt_optimizer = PromptOptimizer()
        self.safety_layer = SafetyLayer()
        self.failover_manager = FailoverManager()
        self.response_validator = ResponseValidator()

        # Registered Provider Adapters
        self.adapters = {
            "mock": MockAdapter(),
            "openai": OpenAIAdapter()
        }
        self._initialized = True
        logger.info("IntelligenceRouter: Central Multi-Model Intelligence Router initialized.")

    async def generate(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        provider: str = "auto",
        model_name: Optional[str] = None,
        task_type: Optional[str] = None,
        memory_context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        task_id: Optional[str] = None,
        expect_json: bool = False
    ) -> ModelResponse:
        """
        Universal Multi-Model Generation Entrypoint for AgentX.
        Classifies task type, selects model, optimizes prompts, verifies safety, executes via adapter,
        handles failover, validates output, and logs database telemetry.
        """
        start_time = time.time()

        # 1. Task Classification
        classified_task = task_type or self.task_classifier.classify(prompt, system_instruction)

        # 2. Model & Provider Selection
        if provider == "auto" or provider in ["FAST_MODEL", "REASONING_MODEL", "CODING_MODEL", "VISION_MODEL"]:
            model_info = self.registry.find_best_model_for_task(classified_task)
            target_provider = model_info["provider"]
            target_model = model_name or model_info["model_name"]
        else:
            target_provider = provider.lower()
            target_model = model_name or "mock-model"

        # 3. Prompt Optimization & Safety Check
        optimized = self.prompt_optimizer.optimize_prompt(
            prompt=prompt,
            system_instruction=system_instruction,
            memory_context=memory_context,
            provider=target_provider
        )
        safety_audit = self.safety_layer.audit_prompt(optimized["prompt"])

        # 4. Resolve Adapter & Execution with Failover
        adapter = self.adapters.get(target_provider)
        if not adapter or not adapter.is_configured():
            # Switch to fallback provider
            fallback_provider = self.failover_manager.get_fallback_provider(target_provider)
            adapter = self.adapters.get(fallback_provider, self.adapters["mock"])
            target_provider = adapter.provider_name

        try:
            response = await adapter.execute(
                prompt=optimized["prompt"],
                system_instruction=optimized["system_instruction"],
                model_name=target_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            self.failover_manager.record_success(target_provider)
        except Exception as e:
            logger.error(f"IntelligenceRouter: Primary execution error on provider '{target_provider}': {e}")
            self.failover_manager.record_failure(target_provider)
            fallback_provider = self.failover_manager.get_fallback_provider(target_provider)
            adapter = self.adapters.get(fallback_provider, self.adapters["mock"])
            response = await adapter.execute(
                prompt=optimized["prompt"],
                system_instruction=optimized["system_instruction"],
                model_name=target_model,
                temperature=temperature,
                max_tokens=max_tokens
            )

        # 5. Response Validation & Metadata Enrichment
        if not safety_audit["safe"]:
            response.safety_flags.extend(safety_audit["flags"])

        response = self.response_validator.validate(response, expect_json=expect_json)
        response.metadata["classified_task"] = classified_task

        # 6. Async Database Telemetry Logging
        await self._log_model_routing(
            task_id=task_id,
            provider=response.provider,
            model_name=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
            status="success" if response.confidence_score > 0 else "failed"
        )

        return response

    async def _log_model_routing(
        self,
        task_id: Optional[str],
        provider: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        latency_ms: int,
        status: str
    ):
        """Persists model metrics database record."""
        try:
            async with async_session() as db:
                log_entry = ModelRouterLog(
                    task_id=uuid.UUID(task_id) if task_id else None,
                    provider=provider,
                    model_name=model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost={"usd": cost_usd},
                    latency_ms=latency_ms,
                    status=status
                )
                db.add(log_entry)
                await db.commit()
        except Exception as e:
            logger.warning(f"IntelligenceRouter: Log writing note: {e}")
