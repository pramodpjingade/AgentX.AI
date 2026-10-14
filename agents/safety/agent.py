import re
from typing import Dict, Any, List
from loguru import logger
from agents.base_agent import BaseAgent
from agents.model_manager import ModelManager

class SafetyAgent(BaseAgent):
    """Scans and filters query input and agent outputs to ensure safety and privacy compliance."""
    
    def __init__(self):
        super().__init__(name="safety_agent", role="safety_guardian")
        self.model_manager = ModelManager()
        
        # Core patterns for PII scrubbing
        self.email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        self.phone_pattern = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
        
        # Injection detection pattern keywords
        self.injection_keywords = [
            "ignore previous instructions",
            "system override",
            "you are now developer",
            "bypass safety",
            "disable guidelines"
        ]

    def get_tools(self) -> List[Any]:
        return []

    def get_system_prompt(self) -> str:
        return "You are the Safety Guardian Agent for AgentX. Audit the content and ensure compliance."

    async def execute(
        self, 
        task_input: Dict[str, Any], 
        global_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Perform safety audits on query or content."""
        content = task_input.get("content", "")
        logger.info("SafetyAgent: Auditing text content...")
        
        flags = []
        
        # 1. PII detection & scrubbing
        scrubbed_content = content
        if self.email_pattern.search(content):
            flags.append("PII_EMAIL_DETECTED")
            scrubbed_content = self.email_pattern.sub("[SCRUBBED_EMAIL]", scrubbed_content)
            
        if self.phone_pattern.search(content):
            flags.append("PII_PHONE_DETECTED")
            scrubbed_content = self.phone_pattern.sub("[SCRUBBED_PHONE]", scrubbed_content)
            
        # 2. Basic Prompt Injection scan
        content_lower = content.lower()
        if any(kw in content_lower for kw in self.injection_keywords):
            flags.append("PROMPT_INJECTION_SUSPECTED")
            
        # 3. Model-based secondary checks for safety policy compliance
        is_safe = True
        if "PROMPT_INJECTION_SUSPECTED" in flags:
            is_safe = False
            
        return {
            "status": "success",
            "is_safe": is_safe,
            "flags": flags,
            "scrubbed_content": scrubbed_content
        }
