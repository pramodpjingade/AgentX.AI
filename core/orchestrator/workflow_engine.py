from loguru import logger

class WorkflowEngine:
    """Manages long-running workflow state machines, coordinating pauses, resumes, and cancels."""
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WorkflowEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        # Store workflow states in memory. Production setups would map this to a shared Redis store.
        self._states = {}
        self._initialized = True
        logger.info("WorkflowEngine initialized.")

    async def register_workflow(self, goal_id: str):
        """Starts monitoring status of an active goal."""
        self._states[goal_id] = "running"
        logger.info(f"WorkflowEngine: Goal '{goal_id}' registered as 'running'.")

    async def pause_workflow(self, goal_id: str) -> bool:
        """Sets active goal state to paused. Auto-registers if not tracked."""
        self._states[goal_id] = "paused"
        logger.info(f"WorkflowEngine: Goal '{goal_id}' set to 'paused'.")
        return True

    async def resume_workflow(self, goal_id: str) -> bool:
        """Resumes a paused goal state back to running. Auto-registers if not tracked."""
        self._states[goal_id] = "running"
        logger.info(f"WorkflowEngine: Goal '{goal_id}' resumed to 'running'.")
        return True

    async def cancel_workflow(self, goal_id: str) -> bool:
        """Aborts and evicts an active goal state. Auto-registers if not tracked."""
        self._states[goal_id] = "cancelled"
        logger.info(f"WorkflowEngine: Goal '{goal_id}' set to 'cancelled'.")
        return True

    async def get_status(self, goal_id: str) -> str:
        """Fetches status of monitored goal."""
        return self._states.get(goal_id, "running")
