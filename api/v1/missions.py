from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Dict, Any

from database.connection import get_db
from database.models import Goal, MissionResult, User
from models.schemas import MissionResultResponse, MissionProgressResponse
from authentication.jwt_handler import get_current_user
from core.orchestrator.response_composer import ResponseComposer

router = APIRouter()

@router.get("/{goal_id}/result", response_model=MissionResultResponse)
async def get_mission_result(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mission Renderer API: Returns ONLY the finalized MissionResult deliverable.
    Does NOT expose internal task execution logs or agent routing states to end users.
    """
    # Verify goal ownership or admin/developer privileges
    goal_stmt = select(Goal).where(Goal.id == goal_id)
    goal_res = await db.execute(goal_stmt)
    goal = goal_res.scalars().first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )

    if current_user.role not in ["admin", "developer"] and goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden. You do not have access to this mission deliverable."
        )

    # Fetch MissionResult
    result_stmt = select(MissionResult).where(MissionResult.goal_id == goal_id)
    res = await db.execute(result_stmt)
    mission_result = res.scalars().first()

    if not mission_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission result is still being generated or is pending."
        )

    return mission_result

@router.get("/{goal_id}/progress", response_model=MissionProgressResponse)
async def get_mission_progress(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns user-friendly progress step and percentage.
    Internal agent names, RAG vectors, and tool execution logs are completely hidden.
    """
    goal_stmt = select(Goal).where(Goal.id == goal_id)
    goal_res = await db.execute(goal_stmt)
    goal = goal_res.scalars().first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )

    if current_user.role not in ["admin", "developer"] and goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden."
        )

    step_msg, percentage = ResponseComposer.get_progress_message(goal.status)

    return {
        "goal_id": goal.id,
        "status": goal.status.upper(),
        "step_message": step_msg,
        "progress_percentage": percentage,
        "updated_at": goal.updated_at
    }

@router.get("/{goal_id}/download")
async def download_mission_result(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Downloads the finalized Mission Result as a Markdown file attachment.
    """
    from fastapi.responses import Response

    goal_stmt = select(Goal).where(Goal.id == goal_id)
    goal_res = await db.execute(goal_stmt)
    goal = goal_res.scalars().first()
    if not goal:
        raise HTTPException(status_code=404, detail="Mission not found")
    if current_user.role not in ["admin", "developer"] and goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")

    result_stmt = select(MissionResult).where(MissionResult.goal_id == goal_id)
    res = await db.execute(result_stmt)
    mission_result = res.scalars().first()
    if not mission_result:
        raise HTTPException(status_code=404, detail="Mission result not yet available.")

    markdown_content = mission_result.markdown_output or f"# {mission_result.title}\n\n{mission_result.summary or 'Mission completed.'}"
    safe_title = goal.title.replace(" ", "_").replace("/", "-")[:50]
    filename = f"AgentX_Mission_{safe_title}.md"

    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
