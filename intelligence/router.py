import os
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
from intelligence.adapters.google_adapter import GoogleGenAIAdapter
from intelligence.adapters.anthropic_adapter import AnthropicAdapter
from intelligence.adapters.ollama_adapter import OllamaAdapter
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
            "openai": OpenAIAdapter(),
            "google": GoogleGenAIAdapter(),
            "anthropic": AnthropicAdapter(),
            "ollama": OllamaAdapter(),
        }
        self._initialized = True
        logger.info("IntelligenceRouter: Central Multi-Model Intelligence Router initialized with multi-provider adapters.")

    def get_configured_providers(self) -> list:
        """Returns list of real providers whose API keys or services are configured."""
        configured = []
        for name in ["google", "openai", "anthropic", "ollama"]:
            adapter = self.adapters.get(name)
            if adapter and adapter.is_configured():
                configured.append(name)
        return configured

    def select_best_provider(self, target_provider: str, classified_task: str) -> tuple[str, str]:
        """
        Selects an appropriate provider and model based on availability and configuration.
        """
        configured = self.get_configured_providers()
        default_env_provider = os.getenv("DEFAULT_LLM_PROVIDER", "").lower().strip()

        # If user explicitly requested mock
        if target_provider == "mock":
            return "mock", "mock-model"

        # If target provider is already configured, use it
        if target_provider in self.adapters and self.adapters[target_provider].is_configured():
            model_info = self.registry.find_best_model_for_task(classified_task, preferred_provider=target_provider)
            return target_provider, model_info.get("model_name", "default")

        # If default env provider is configured, prioritize it
        if default_env_provider in self.adapters and self.adapters[default_env_provider].is_configured():
            model_info = self.registry.find_best_model_for_task(classified_task, preferred_provider=default_env_provider)
            return default_env_provider, model_info.get("model_name", "default")

        # Prioritize any other configured provider (Google, OpenAI, Anthropic, Ollama)
        for p in ["google", "openai", "anthropic", "ollama"]:
            if p in configured:
                model_info = self.registry.find_best_model_for_task(classified_task, preferred_provider=p)
                return p, model_info.get("model_name", "default")

        # If mock mode is explicitly permitted
        if target_provider == "mock" or os.getenv("AGENTX_ALLOW_MOCK", "").lower() in ["1", "true", "yes"]:
            return "mock", "mock-model"

        # Otherwise target provider requested (will produce clean missing-key configuration message)
        fallback = target_provider if target_provider in self.adapters else "openai"
        return fallback, "default"

    async def generate(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        provider: str = "auto",
        model_name: Optional[str] = None,
        task_type: Optional[str] = None,
        memory_context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
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
        raw_provider = provider.lower() if provider else "auto"
        if raw_provider in ["auto", "fast_model", "reasoning_model", "coding_model", "vision_model"]:
            model_info = self.registry.find_best_model_for_task(classified_task)
            ideal_provider = model_info["provider"]
            target_provider, auto_model = self.select_best_provider(ideal_provider, classified_task)
            target_model = model_name or auto_model
        elif raw_provider in self.adapters:
            target_provider = raw_provider
            target_model = model_name or "default"
        else:
            # Unsupported or unknown explicit provider specified
            target_provider = raw_provider
            target_model = model_name or "default"

        # 3. Prompt Optimization & Safety Check
        optimized = self.prompt_optimizer.optimize_prompt(
            prompt=prompt,
            system_instruction=system_instruction,
            memory_context=memory_context,
            provider=target_provider
        )
        safety_audit = self.safety_layer.audit_prompt(optimized["prompt"])

        # 4. Resolve Adapter & Execution
        adapter = self.adapters.get(target_provider)
        if not adapter:
            if target_provider == "mock":
                adapter = self.adapters["mock"]
            else:
                return ModelResponse(
                    response_text=f"[Model Provider Error ({target_provider})] Provider '{target_provider}' is not supported.",
                    provider=target_provider,
                    model=target_model,
                    confidence_score=0.0,
                    finish_reason="error",
                    safety_flags=[f"UnsupportedProvider: {target_provider}"]
                )

        # Check configuration
        if not adapter.is_configured() and target_provider != "mock":
            # Check if any other provider is configured to failover to
            configured = self.get_configured_providers()
            if configured:
                fallback_name = configured[0]
                adapter = self.adapters[fallback_name]
                target_provider = fallback_name
                logger.info(f"IntelligenceRouter: Switched to configured provider '{target_provider}'")
            else:
                # No keys configured anywhere and mock not requested:
                # Provide an informative configuration response (never fabricate fake output)
                logger.warning(f"IntelligenceRouter: No configured LLM provider found for target '{target_provider}'.")
                response = ModelResponse(
                    response_text=(
                        "**[AgentX Configuration Required]**\n\n"
                        "AgentX requires an active language model provider to process your request.\n\n"
                        "Please configure one of the following in your `.env` file:\n"
                        "- **Google Gemini:** `GOOGLE_API_KEY=your-gemini-api-key`\n"
                        "- **OpenAI:** `OPENAI_API_KEY=your-openai-api-key`\n"
                        "- **Anthropic Claude:** `ANTHROPIC_API_KEY=your-anthropic-api-key`\n"
                        "- **Local Ollama:** Set `OLLAMA_ENABLED=true` with Ollama running at `http://localhost:11434`\n\n"
                        "Once configured, AgentX will automatically route requests to your model."
                    ),
                    provider=target_provider,
                    model=target_model,
                    confidence_score=0.0,
                    finish_reason="error",
                    safety_flags=["MISSING_CREDENTIALS"]
                )
                await self._log_model_routing(
                    task_id=task_id,
                    provider=target_provider,
                    model_name=target_model,
                    prompt_tokens=len(prompt) // 4,
                    completion_tokens=0,
                    cost_usd=0.0,
                    latency_ms=0,
                    status="failed"
                )
                return response

        try:
            response = await adapter.execute(
                prompt=optimized["prompt"],
                system_instruction=optimized["system_instruction"],
                model_name=target_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            if response.finish_reason != "error":
                self.failover_manager.record_success(target_provider)
            else:
                self.failover_manager.record_failure(target_provider)
        except Exception as e:
            logger.error(f"IntelligenceRouter: Execution error on provider '{target_provider}': {e}")
            self.failover_manager.record_failure(target_provider)
            response = ModelResponse(
                response_text=f"[Model Provider Error ({target_provider})] {str(e)}",
                latency_ms=int((time.time() - start_time) * 1000),
                provider=target_provider,
                model=target_model,
                confidence_score=0.0,
                finish_reason="error",
                safety_flags=[f"ProviderError: {e}"]
            )

        # 5. Response Validation & Metadata Enrichment
        if not safety_audit["safe"]:
            response.safety_flags.extend(safety_audit["flags"])

        response = self.response_validator.validate(response, expect_json=expect_json)
        response.metadata["classified_task"] = classified_task

        # 6. Async Database Telemetry Logging
        try:
            await self._log_model_routing(
                task_id=task_id,
                provider=response.provider,
                model_name=response.model,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                cost_usd=response.cost_usd,
                latency_ms=response.latency_ms,
                status="success" if response.finish_reason != "error" else "failed"
            )
        except Exception as log_err:
            logger.debug(f"IntelligenceRouter: Telemetry logging note: {log_err}")

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

    async def stream(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        provider: str = "auto",
        model_name: Optional[str] = None,
        task_type: Optional[str] = None,
        memory_context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        """
        Universal Multi-Model Streaming Entrypoint for AgentX.
        Yields raw text tokens directly from the selected adapter.
        """
        classified_task = task_type or self.task_classifier.classify(prompt, system_instruction)
        raw_provider = provider.lower() if provider else "auto"

        if raw_provider in ["auto", "fast_model", "reasoning_model", "coding_model", "vision_model"]:
            model_info = self.registry.find_best_model_for_task(classified_task)
            ideal_provider = model_info["provider"]
            target_provider, auto_model = self.select_best_provider(ideal_provider, classified_task)
            target_model = model_name or auto_model
        elif raw_provider in self.adapters:
            target_provider = raw_provider
            target_model = model_name or "default"
        else:
            target_provider, auto_model = self.select_best_provider("auto", classified_task)
            target_model = model_name or auto_model

        optimized = self.prompt_optimizer.optimize_prompt(
            prompt=prompt,
            system_instruction=system_instruction,
            memory_context=memory_context,
            provider=target_provider
        )

        adapter = self.adapters.get(target_provider)
        if not adapter:
            adapter = self.adapters["mock"]
            target_provider = "mock"

        if not adapter.is_configured() and target_provider != "mock":
            configured = self.get_configured_providers()
            if configured:
                target_provider = configured[0]
                adapter = self.adapters[target_provider]
            else:
                yield (
                    "**[AgentX Configuration Required]**\n\n"
                    "AgentX requires an active language model provider to process your request.\n\n"
                    "Please configure one of the following in your `.env` file:\n"
                    "- **Google Gemini:** `GOOGLE_API_KEY=your-gemini-api-key`\n"
                    "- **OpenAI:** `OPENAI_API_KEY=your-openai-api-key`\n"
                    "- **Anthropic Claude:** `ANTHROPIC_API_KEY=your-anthropic-api-key`\n"
                    "- **Local Ollama:** Set `OLLAMA_ENABLED=true` with Ollama running at `http://localhost:11434`\n\n"
                    "Once configured, AgentX will automatically route requests to your model."
                )
                return

        try:
            async for token in adapter.stream(
                prompt=optimized["prompt"],
                system_instruction=optimized["system_instruction"],
                model_name=target_model,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                yield token
        except Exception as e:
            logger.error(f"IntelligenceRouter streaming failure: {e}")
            yield f"[Model Provider Error ({target_provider})] {str(e)}"
