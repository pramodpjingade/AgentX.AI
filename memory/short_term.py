import os
import json
from typing import Optional, Dict, Any
import redis.asyncio as aioredis
from loguru import logger

class ShortTermMemory:
    """Manages active session cache using Redis, falling back to local memory if offline."""
    
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/0"
        
        self.client: Optional[aioredis.Redis] = None
        self.local_cache: Dict[str, str] = {}
        self.use_fallback = False
        
        # Test connection asynchronously during first access or lazy initialization
        self._initialized = False

    async def _init_client(self):
        if self._initialized:
            return
            
        try:
            # Try to connect with 1 second timeout to avoid blocking startup
            self.client = aioredis.from_url(
                self.redis_url, 
                socket_timeout=1.0, 
                decode_responses=True
            )
            await self.client.ping()
            logger.info(f"ShortTermMemory: Successfully connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.warning(f"ShortTermMemory: Redis connection failed: {e}. Falling back to in-memory cache.")
            self.use_fallback = True
            
        self._initialized = True

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session dictionary state."""
        await self._init_client()
        
        if self.use_fallback:
            data = self.local_cache.get(session_id)
        else:
            try:
                data = await self.client.get(session_id)
            except Exception as e:
                logger.error(f"ShortTermMemory: Redis GET error: {e}. Reading from local fallback.")
                data = self.local_cache.get(session_id)
                
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None

    async def set_session(self, session_id: str, data: Dict[str, Any], expire: int = 3600):
        """Save session state with an expiration TTL."""
        await self._init_client()
        serialized = json.dumps(data)
        
        # Always update local cache as a redundant backup
        self.local_cache[session_id] = serialized
        
        if not self.use_fallback:
            try:
                await self.client.set(session_id, serialized, ex=expire)
            except Exception as e:
                logger.error(f"ShortTermMemory: Redis SET error: {e}.")

    async def delete_session(self, session_id: str):
        """Remove a session from cache."""
        await self._init_client()
        if session_id in self.local_cache:
            del self.local_cache[session_id]
            
        if not self.use_fallback:
            try:
                await self.client.delete(session_id)
            except Exception as e:
                logger.error(f"ShortTermMemory: Redis DELETE error: {e}.")
                
# Global short term memory manager singleton
short_term_memory = ShortTermMemory()
