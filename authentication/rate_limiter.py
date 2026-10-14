import time
from fastapi import Request, HTTPException, status
from loguru import logger

from memory.short_term import short_term_memory

class RateLimiter:
    """Limits the number of requests a client can make within a specified time window."""
    
    def __init__(self, requests_limit: int = 1000, window_seconds: int = 60):
        self.limit = requests_limit
        self.window = window_seconds

    async def check_rate_limit(self, request: Request):
        """FastAPI dependency to enforce request limits per client IP."""
        client_ip = request.client.host if request.client else "unknown_ip"
        if client_ip in ("127.0.0.1", "localhost", "::1"):
            return
            
        key = f"rate_limit:{client_ip}"
        
        # Retrieve current count list
        history = await short_term_memory.get_session(key) or []
        current_time = time.time()
        
        # Filter out timestamps older than our sliding window
        history = [ts for ts in history if current_time - ts < self.window]
        
        if len(history) >= self.limit:
            logger.warning(f"RateLimit: IP {client_ip} has exceeded the rate limit threshold ({self.limit} reqs/{self.window}s).")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
            
        # Record new hit
        history.append(current_time)
        # Store back in cache with window-sized TTL
        await short_term_memory.set_session(key, history, expire=self.window)
