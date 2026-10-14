from typing import Dict, Any
from loguru import logger

class TaskClassifier:
    """
    Task Classifier for AgentX (Phase 5 Intelligence Router).
    Analyzes prompt text, instructions, and context to classify task domain type:
    coding, reasoning, research, planning, vision, audio, translation, rag, or general.
    """

    @staticmethod
    def classify(prompt: str, system_instruction: str = "") -> str:
        """Classifies prompt and instructions into task domain category."""
        text = (prompt + " " + system_instruction).lower()

        if any(w in text for w in ["code", "python", "script", "function", "lint", "fastapi", "bug", "refactor"]):
            return "coding"
        elif any(w in text for w in ["plan", "decompose", "strategy", "complexity", "risk"]):
            return "reasoning"
        elif any(w in text for w in ["image", "photo", "picture", "vision", "ocr"]):
            return "vision"
        elif any(w in text for w in ["search", "gather", "research", "facts", "citations"]):
            return "research"
        elif any(w in text for w in ["translate", "language", "french", "spanish"]):
            return "translation"
        elif any(w in text for w in ["vector", "rag", "retrieved", "documents"]):
            return "rag"
        else:
            return "general"
