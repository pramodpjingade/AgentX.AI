from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from database.models import User, Goal
from database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from authentication.jwt_handler import get_current_user
from core.orchestrator.workflow_engine import WorkflowEngine

router = APIRouter()
engine = WorkflowEngine()

@router.get("/status/{goal_id}")
async def get_workflow_status(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches the active runtime status of a given workflow goal."""
    # Enforce authorization checks
    stmt = select(Goal).where(Goal.id == goal_id)
    res = await db.execute(stmt)
    goal = res.scalars().first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found."
        )
    
    if current_user.role not in ["admin", "developer"] and goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Access restricted."
        )

    state = await engine.get_status(str(goal_id))
    return {"goal_id": goal_id, "status": state}

@router.post("/pause/{goal_id}")
async def pause_workflow(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pauses an active workflow task loop."""
    stmt = select(Goal).where(Goal.id == goal_id)
    res = await db.execute(stmt)
    goal = res.scalars().first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found."
        )

    if current_user.role not in ["admin", "developer"] and goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Access restricted."
        )

    success = await engine.pause_workflow(str(goal_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active goal '{goal_id}' not found in runtime registry."
        )
    
    # Update status in database
    goal.status = "paused"
    await db.commit()

    return {"goal_id": goal_id, "status": "paused"}

@router.post("/resume/{goal_id}")
async def resume_workflow(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resumes execution of a paused workflow task loop."""
    stmt = select(Goal).where(Goal.id == goal_id)
    res = await db.execute(stmt)
    goal = res.scalars().first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found."
        )

    if current_user.role not in ["admin", "developer"] and goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Access restricted."
        )

    success = await engine.resume_workflow(str(goal_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active goal '{goal_id}' not found in runtime registry."
        )
    
    # Update status in database
    goal.status = "executing"
    await db.commit()

    return {"goal_id": goal_id, "status": "running"}

@router.post("/cancel/{goal_id}")
async def cancel_workflow(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aborts and cancels execution of an active workflow."""
    stmt = select(Goal).where(Goal.id == goal_id)
    res = await db.execute(stmt)
    goal = res.scalars().first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found."
        )

    if current_user.role not in ["admin", "developer"] and goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Access restricted."
        )

    success = await engine.cancel_workflow(str(goal_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active goal '{goal_id}' not found in runtime registry."
        )
    
    # Update status in database
    goal.status = "cancelled"
    await db.commit()

    return {"goal_id": goal_id, "status": "cancelled"}
