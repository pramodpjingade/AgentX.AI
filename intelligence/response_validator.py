import json
from typing import Dict, Any, Optional
from loguru import logger
from intelligence.response_object import ModelResponse

class ResponseValidator:
    """
    Response Validator & Quality Auditor for AgentX.
    Validates model response completeness, JSON schema parsing, and confidence scoring.
    """

    @staticmethod
    def validate(response: ModelResponse, expect_json: bool = False) -> ModelResponse:
        """Audits response payload and populates structured_json / confidence_score."""
        if not response.response_text or not response.response_text.strip():
            response.confidence_score = 0.0
            response.finish_reason = "error"
            return response

        # Try JSON parsing if requested or if output looks like JSON
        cleaned = response.response_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if len(lines) > 2:
                cleaned = "\n".join(lines[1:-1])

        if expect_json or cleaned.startswith("{") or cleaned.startswith("["):
            try:
                response.structured_json = json.loads(cleaned.strip())
                response.confidence_score = 0.98
            except Exception:
                if expect_json:
                    response.confidence_score = 0.50
                    response.safety_flags.append("InvalidJSONFormat")

        return response
