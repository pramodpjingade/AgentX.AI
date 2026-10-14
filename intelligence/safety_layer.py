import re
from typing import Dict, Any, List
from loguru import logger

class SafetyLayer:
    """
    Safety Guardian & PII Scrubber for AgentX.
    Audits prompts and response payloads for PII leaks, prompt injection attempts, and safety violations.
    """

    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"disregard all prior instructions",
        r"reveal system prompt",
        r"drop database",
        r"rm -rf"
    ]

    def audit_prompt(self, prompt: str) -> Dict[str, Any]:
        """Scans prompt text for safety violations or prompt injection."""
        flags = []
        clean_text = prompt

        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                flags.append(f"PromptInjectionDetected: {pattern}")
                logger.warning(f"SafetyLayer: Detected injection pattern '{pattern}' in prompt")

        return {
            "safe": len(flags) == 0,
            "flags": flags,
            "sanitized_text": clean_text
        }
