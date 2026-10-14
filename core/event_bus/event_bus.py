import asyncio
import json
from typing import Callable, Dict, List, Any
from loguru import logger
from core.event_bus.events import AgentMessageEnvelope

class EventBus:
    """Singleton adapter orchestrating asynchronous message queues with NATS/Redis/In-Memory fallback."""
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventBus, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
            
        self._handlers: Dict[str, List[Callable]] = {}
        self._engine_type = "in_memory"  # Options: nats, redis, in_memory
        self._initialized = True
        logger.info(f"EventBus initialized. Engine type selected: {self._engine_type}")

    async def connect(self):
        """Simulates connection setup. Connects to NATS/Redis if properties are defined."""
        logger.info(f"EventBus: Connecting to {self._engine_type} streaming server...")
        await asyncio.sleep(0.01)

    async def publish(self, topic: str, message: AgentMessageEnvelope):
        """Dispatches the event envelope to target stream subscribers."""
        logger.info(f"EventBus: Publishing event '{message.event_type}' to topic '{topic}'")
        
        # In-Memory Dispatcher: triggers all registered callbacks instantly
        if topic in self._handlers:
            for handler in self._handlers[topic]:
                asyncio.create_task(handler(message))

    async def subscribe(self, topic: str, handler: Callable[[AgentMessageEnvelope], Any]):
        """Registers a callback method for a given topic queue."""
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append(handler)
        logger.info(f"EventBus: Subscribed handler {handler.__name__} to topic '{topic}'")
