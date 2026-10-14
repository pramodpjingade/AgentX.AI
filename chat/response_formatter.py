import re
from typing import Dict, Any, List, Optional
from loguru import logger
from database.models import MissionResult

class ResponseFormatter:
    """
    Response Formatter for AgentX Chat Layer.
    Transforms raw MissionResult and internal multi-agent outputs into clean, readable
    assistant markdown text without exposing raw logs, internal agent names, or stacktraces to users.
    """

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        """Strips internal agent names, raw JSON blobs, debug headers, and internal traces."""
        if not text:
            return ""

        output = str(text)

        # 1. Remove debug / system header banners and emojis
        output = re.sub(r'(?i).*?AgentX AI OS Executive Synthesis.*?\n', '', output)
        output = re.sub(r'(?i)#*\s*Here is your completed mission deliverable:.*?\n', '', output)
        output = re.sub(r'---\s*Agent Result.*?\n', '', output)
        output = re.sub(r'\[\d{1,2}:\d{2}:\d{2}.*?\]\s*.*?Agent:.*?\n', '', output)

        # 2. Remove raw Python dictionary lines (e.g., {'status': 'success', ...})
        lines = []
        for line in output.split('\n'):
            stripped = line.strip()
            if stripped.startswith("{'status':") or stripped.startswith('{"status":') or stripped.startswith("{'is_safe':") or stripped.startswith('{"is_safe":'):
                continue
            if stripped.startswith('--- Agent Result') or stripped.startswith('--- Subtask Result'):
                continue
            lines.append(line)
        output = '\n'.join(lines)

        # 3. Remove internal agent names if present in system text
        agent_names_pattern = r'\b(safety_agent|intent_agent|planning_agent|master_agent|router_agent|evaluator_agent|education_agent|travel_agent|coding_agent|research_agent|fact_verification_agent|governance_layer|evaluation_agent)\b'
        output = re.sub(agent_names_pattern, 'assistant', output, flags=re.IGNORECASE)

        # 4. Clean up raw JSON dumps if they are not code blocks requested by user
        if output.strip().startswith('{') and output.strip().endswith('}'):
            try:
                import json
                data = json.loads(output)
                if isinstance(data, dict):
                    if data.get('content'):
                        output = str(data['content'])
                    elif data.get('summary'):
                        output = str(data['summary'])
                    elif data.get('deliverable'):
                        deliv = data['deliverable']
                        if isinstance(deliv, dict):
                            output = deliv.get('content') or deliv.get('summary') or str(deliv)
                        else:
                            output = str(deliv)
            except Exception:
                pass

        return output.strip()

    @classmethod
    def format_mission_result(cls, mission_result: Optional[MissionResult], goal_title: str) -> str:
        """Formats MissionResult into a clean ChatGPT-style response."""
        if not mission_result:
            return f"I have processed your request for **{goal_title}**."

        raw = ""
        if getattr(mission_result, "markdown_output", None):
            raw = mission_result.markdown_output
        elif getattr(mission_result, "summary", None):
            raw = mission_result.summary
        else:
            composed = getattr(mission_result, "composed_result", {}) or {}
            if isinstance(composed, dict):
                deliv = composed.get("deliverable") or composed.get("structured_output")
                if isinstance(deliv, str):
                    raw = deliv
                elif isinstance(deliv, dict):
                    raw = deliv.get("content") or deliv.get("summary") or str(deliv)
                elif composed.get("summary"):
                    raw = composed["summary"]

        if not raw:
            raw = f"Here is the completed deliverable for **{goal_title}**."

        return cls.sanitize_output(raw)

    @staticmethod
    def format_error_response(error_message: str) -> str:
        """Formats errors into a polite, user-friendly assistant response."""
        logger.warning(f"ResponseFormatter: Formatting internal error: {error_message}")
        return (
            "I encountered an unexpected issue while processing your request. "
            "Our system has recorded this event to ensure continuous performance. "
            "Please try submitting your question again."
        )

