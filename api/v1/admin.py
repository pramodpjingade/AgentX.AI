from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime

from database.connection import get_db
from database.models import User, ModelRouterLog, Goal
from authentication.jwt_handler import get_current_user

router = APIRouter()

# Schema definitions
class UserAdminResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class RoleUpdateSchema(BaseModel):
    role: str  # admin, developer, user

class SystemMetricsResponse(BaseModel):
    total_users: int
    total_goals: int
    total_model_calls: int
    database_type: str

class AuditLogResponse(BaseModel):
    id: UUID
    provider: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Helper dependency to enforce admin role
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Administrative access required."
        )
    return current_user

@router.get("/users", response_model=List[UserAdminResponse], dependencies=[Depends(require_admin)])
async def admin_list_users(db: AsyncSession = Depends(get_db)):
    """List all registered users in the platform."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())

@router.put("/users/{user_id}/role", response_model=UserAdminResponse, dependencies=[Depends(require_admin)])
async def admin_update_user_role(
    user_id: UUID,
    payload: RoleUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Change a user's role (admin, developer, user)."""
    if payload.role not in ["admin", "developer", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'admin', 'developer', or 'user'."
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = payload.role
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/system/metrics", response_model=SystemMetricsResponse, dependencies=[Depends(require_admin)])
async def admin_system_metrics(db: AsyncSession = Depends(get_db)):
    """Retrieve database metrics and health stats."""
    import os
    
    # Query totals
    users_count = await db.execute(select(User))
    goals_count = await db.execute(select(Goal))
    logs_count = await db.execute(select(ModelRouterLog))
    
    db_url = os.getenv("DATABASE_URL", "")
    db_type = "sqlite" if db_url.startswith("sqlite") else "postgres"
    
    return {
        "total_users": len(users_count.scalars().all()),
        "total_goals": len(goals_count.scalars().all()),
        "total_model_calls": len(logs_count.scalars().all()),
        "database_type": db_type
    }

@router.get("/audit-logs", response_model=List[AuditLogResponse], dependencies=[Depends(require_admin)])
async def admin_audit_logs(db: AsyncSession = Depends(get_db)):
    """Retrieve recent model routing logs as platform audit logs."""
    result = await db.execute(
        select(ModelRouterLog)
        .order_by(ModelRouterLog.created_at.desc())
        .limit(100)
    )
    return list(result.scalars().all())
