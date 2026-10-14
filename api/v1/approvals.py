from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database.connection import get_db
from database.models import ApprovalRequest, User
from authentication.jwt_handler import get_current_user

router = APIRouter()

# Schema definitions
class ApprovalRequestCreateSchema(BaseModel):
    task_id: Optional[UUID] = None
    agent_name: str
    tool_name: str
    parameters: Optional[dict] = {}

class ApprovalResolutionSchema(BaseModel):
    action: str  # approved, rejected

class ApprovalResponseSchema(BaseModel):
    id: UUID
    task_id: Optional[UUID]
    agent_name: str
    tool_name: str
    parameters: dict
    status: str
    resolved_by: Optional[UUID]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ApprovalResponseSchema])
async def list_approvals(
    status_filter: Optional[str] = "pending",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists authorization requests filtered by status."""
    if current_user.role not in ["admin", "developer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admins or developers can view approvals."
        )
    stmt = select(ApprovalRequest)
    if status_filter:
        stmt = stmt.where(ApprovalRequest.status == status_filter)
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.post("/request", response_model=ApprovalResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_approval_request(
    payload: ApprovalRequestCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new pending tool approval request."""
    new_request = ApprovalRequest(
        task_id=payload.task_id,
        agent_name=payload.agent_name,
        tool_name=payload.tool_name,
        parameters=payload.parameters,
        status="pending"
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return new_request

@router.post("/resolve/{approval_id}", response_model=ApprovalResponseSchema)
async def resolve_approval(
    approval_id: UUID,
    payload: ApprovalResolutionSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolves a pending approval action as approved or rejected."""
    # Ensure current user is admin or developer/operator
    if current_user.role not in ["admin", "developer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admins or developers can resolve approvals."
        )

    stmt = select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
    result = await db.execute(stmt)
    request = result.scalars().first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request '{approval_id}' not found."
        )

    if request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval request '{approval_id}' has already been resolved."
        )

    action_lower = payload.action.lower()
    if action_lower not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'approved' or 'rejected'."
        )

    request.status = action_lower
    request.resolved_by = current_user.id
    request.resolved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(request)
    return request
