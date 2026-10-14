from typing import List, Dict, Any

class MasterAgentMemory:
    """Manages short-term episodic memory logs for the Master Agent."""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add_episode(self, task_id: str, action: str, result: Any):
        """Append an execution history record."""
        self.history.append({
            "task_id": task_id,
            "action": action,
            "result": result
        })

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieve execution history logs."""
        return self.history
