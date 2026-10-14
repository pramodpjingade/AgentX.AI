from fastapi import APIRouter
from api.v1.auth import router as auth_router
from api.v1.goals import router as goals_router
from api.v1.missions import router as missions_router
from api.v1.websockets import router as ws_router
from api.v1.plugins import router as plugins_router
from api.v1.approvals import router as approvals_router
from api.v1.workflows import router as workflows_router
from api.v1.admin import router as admin_router

from chat.router import router as chat_router

api_router = APIRouter()

# Register sub-routes
api_router.include_router(chat_router, prefix="/chat", tags=["Professional Chat Gateway"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(goals_router, prefix="/goals", tags=["Goal Planner"])
api_router.include_router(missions_router, prefix="/missions", tags=["Mission Renderer Engine"])
api_router.include_router(ws_router, prefix="/ws", tags=["Real-time Stream"])
api_router.include_router(plugins_router, prefix="/plugins", tags=["Plugin Marketplace"])
api_router.include_router(approvals_router, prefix="/approvals", tags=["HITL Approvals Queue"])
api_router.include_router(workflows_router, prefix="/workflows", tags=["Workflow Control Engine"])
api_router.include_router(admin_router, prefix="/admin", tags=["Platform Administration"])
