import re
from typing import Dict, Any, List, Optional
from loguru import logger
from database.models import MissionResult

class ResponseFormatter:
    """
    Response Formatter for AgentX Chat Layer.
    Transforms raw MissionResult and multi-agent outputs into clean, readable
    assistant markdown text without exposing raw logs, internal agent names,
    task assignment dictionaries, or stacktraces to users.
    """

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        """Strips internal agent names, raw JSON blobs, debug headers, and internal traces."""
        if not text:
            return ""

        output = str(text).strip()

        # 1. Remove debug / system header banners
        output = re.sub(r'(?i).*?AgentX AI OS Executive Synthesis.*?\n', '', output)
        output = re.sub(r'(?i)#*\s*Here is your completed mission deliverable:.*?\n', '', output)
        output = re.sub(r'---\s*Agent Result.*?\n', '', output)
        output = re.sub(r'---\s*Subtask Result.*?\n', '', output)
        output = re.sub(r'\[\d{1,2}:\d{2}:\d{2}.*?\]\s*.*?Agent:.*?\n', '', output)

        # 2. Remove raw Python dictionary lines (e.g., {'status': 'success', ...})
        lines = []
        for line in output.split('\n'):
            stripped = line.strip()
            if (stripped.startswith("{'status':") or stripped.startswith('{"status":') or 
                stripped.startswith("{'is_safe':") or stripped.startswith('{"is_safe":') or
                stripped.startswith("{'task_id':") or stripped.startswith('{"task_id":') or
                stripped.startswith("{'goal_id':") or stripped.startswith('{"goal_id":')):
                continue
            if stripped.startswith('--- Agent Result') or stripped.startswith('--- Subtask Result'):
                continue
            lines.append(line)
        output = '\n'.join(lines).strip()

        # 3. Clean up raw JSON dumps if accidentally produced outside code blocks
        if output.startswith('{') and output.endswith('}') and not ('\n```' in output):
            try:
                import json
                data = json.loads(output)
                if isinstance(data, dict):
                    if data.get('content'):
                        output = str(data['content'])
                    elif data.get('result'):
                        output = str(data['result'])
                    elif data.get('summary'):
                        output = str(data['summary'])
                    elif data.get('deliverable'):
                        deliv = data['deliverable']
                        if isinstance(deliv, dict):
                            output = deliv.get('content') or deliv.get('summary') or ""
                        elif isinstance(deliv, str):
                            output = deliv
            except Exception:
                pass

        # 4. Remove internal agent names from free text if present in prompt leakages
        agent_names_pattern = r'\b(safety_agent|intent_agent|planning_agent|master_agent|router_agent|evaluator_agent|education_agent|travel_agent|coding_agent|research_agent|fact_verification_agent|governance_layer|evaluation_agent)\b'
        output = re.sub(agent_names_pattern, 'assistant', output, flags=re.IGNORECASE)

        return output.strip()

    @classmethod
    def format_mission_result(cls, mission_result: Optional[MissionResult], goal_title: str) -> str:
        """Formats MissionResult into a clean, comprehensive assistant response."""
        if not mission_result:
            return f"I have processed your request for **{goal_title}**."

        raw = ""

        # 1. Check primary markdown_output
        if getattr(mission_result, "markdown_output", None) and str(mission_result.markdown_output).strip():
            raw = str(mission_result.markdown_output).strip()

        # 2. Check composed_result
        if not raw:
            composed = getattr(mission_result, "composed_result", {}) or {}
            if isinstance(composed, dict):
                if composed.get("markdown_output") and str(composed["markdown_output"]).strip():
                    raw = str(composed["markdown_output"]).strip()
                elif composed.get("deliverable"):
                    deliv = composed["deliverable"]
                    if isinstance(deliv, dict):
                        raw = deliv.get("content") or deliv.get("report_body") or deliv.get("summary") or ""
                    elif isinstance(deliv, str):
                        raw = deliv
                elif composed.get("summary"):
                    raw = composed["summary"]

        # 3. Check summary field on model
        if not raw and getattr(mission_result, "summary", None):
            raw = str(mission_result.summary).strip()

        if not raw or raw.startswith("{'"):
            raw = f"Completed operations for **{goal_title}**."

        return cls.sanitize_output(raw)

    @staticmethod
    def format_error_response(error_message: str) -> str:
        """Formats errors into a polite, user-friendly assistant response."""
        logger.warning(f"ResponseFormatter: Formatting internal error: {error_message}")
        return (
            f"I encountered an issue processing your request: {error_message}. "
            "Please verify your configuration and try again."
        )
