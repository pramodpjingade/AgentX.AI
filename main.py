import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from api.router import api_router
from database.connection import engine
from authentication.rate_limiter import RateLimiter

load_dotenv()

app = FastAPI(
    title="AgentX Backend Engine",
    description="Advanced Autonomous Multi-Agent AI Ecosystem Core API Gateway",
    version="1.1.0"
)

# Initialize Rate Limiter
limiter = RateLimiter(requests_limit=1000, window_seconds=60)

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Global sliding window rate limiting middleware."""
    if request.url.path.endswith("/health"):
        return await call_next(request)
        
    try:
        await limiter.check_rate_limit(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Rate limiter error: {e}"})
        
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["Diagnostic"])
async def health_check():
    """System health check endpoint."""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.1.0",
        "database": "sqlite" if os.environ.get("DATABASE_URL", "").startswith("sqlite") else "postgres",
        "agents_online": 19
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to format errors uniformly."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "error_type": type(exc).__name__,
            "message": str(exc)
        }
    )

@app.on_event("startup")
async def startup_event():
    """Bootstrap the event worker and subscribe to topics."""
    from core.event_bus.event_bus import EventBus
    from core.orchestrator.event_worker import OrchestratorEventWorker
    from database.init_db import seed_development_accounts
    from loguru import logger
    
    # Seed development accounts
    try:
        await seed_development_accounts()
        logger.info("FastAPI startup: Seeding development accounts check completed.")
    except Exception as e:
        logger.error(f"FastAPI startup: Error seeding development accounts: {e}")
    
    event_bus = EventBus()
    await event_bus.connect()
    
    worker = OrchestratorEventWorker()
    await worker.start()
    logger.info("FastAPI startup: OrchestratorEventWorker initialized and listening.")

@app.on_event("shutdown")
async def shutdown_event():
    """Dispose database connections on app shutdown."""
    await engine.dispose()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
