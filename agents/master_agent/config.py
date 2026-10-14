import os

class MasterAgentConfig:
    """Configuration settings for the Master Agent."""
    
    NAME = "master_agent"
    ROLE = "Ecosystem CEO & Dynamic Task Coordinator"
    
    # Model settings
    DEFAULT_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "mock")
    DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "mock-model")
    
    # Execution constraints
    MAX_RETRIES = 3
    TEMPERATURE = 0.2
