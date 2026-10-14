from typing import List, Dict, Any

class MasterAgentTools:
    """Helper tools accessible by the Master Agent."""
    
    @staticmethod
    def get_tools_list() -> List[Dict[str, Any]]:
        """Return descriptors of tools available to Master Agent."""
        return [
            {
                "name": "delegate_task",
                "description": "Delegates a sub-task to a specialized agent.",
                "parameters": ["assigned_agent", "input_data"]
            },
            {
                "name": "notify_user",
                "description": "Sends a message notification to the user.",
                "parameters": ["message"]
            }
        ]
