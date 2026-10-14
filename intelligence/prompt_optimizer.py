from typing import Dict, Any, Optional

class PromptOptimizer:
    """
    Prompt Optimizer & Context Injector for AgentX.
    Enhances raw prompts with cognitive memory, RAG context, system instructions,
    and provider-specific formatting guidelines.
    """

    @staticmethod
    def optimize_prompt(
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        memory_context: Optional[Dict[str, Any]] = None,
        provider: str = "openai"
    ) -> Dict[str, str]:
        """
        Builds optimized system instruction and user prompt text.
        """
        from datetime import datetime
        now = datetime.now()
        time_ctx = f"\n[Current Date & Time: {now.strftime('%A, %B %d, %Y %I:%M:%S %p')}]"
        optimized_sys = system_instruction.strip() + time_ctx
        optimized_prompt = prompt.strip()

        if memory_context:
            rag_context = memory_context.get("rag_context")
            preferences = memory_context.get("preferences")

            if rag_context:
                optimized_prompt = f"[Retrieved RAG Context]\n{rag_context}\n\n[User Goal]\n{optimized_prompt}"

            if preferences:
                pref_str = "\n".join([f"- {p}" for p in preferences[:3]])
                optimized_sys += f"\n\n[Learned User Preferences]\n{pref_str}"

        # Provider specific formatting hints
        if provider.lower() == "anthropic":
            optimized_sys += "\nBe concise, precise, and use clean markdown."

        return {
            "system_instruction": optimized_sys,
            "prompt": optimized_prompt
        }
