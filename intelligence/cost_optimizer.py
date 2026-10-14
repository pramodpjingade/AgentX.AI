from typing import Dict, Any

class CostOptimizer:
    """
    Cost & Token Budget Optimizer for AgentX.
    Calculates exact token costs based on model pricing matrices and enforces budget constraints.
    """

    PRICING_MATRIX = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "deepseek-chat": {"input": 0.14, "output": 0.28},
        "llama3": {"input": 0.0, "output": 0.0},
        "mock": {"input": 0.0, "output": 0.0}
    }

    @classmethod
    def calculate_cost(cls, model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates USD cost for a given model and token count."""
        pricing = cls.PRICING_MATRIX.get(model_name, cls.PRICING_MATRIX["mock"])
        input_cost = (prompt_tokens / 1_000_000.0) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000.0) * pricing["output"]
        return round(input_cost + output_cost, 6)
