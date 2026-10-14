from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List

from database.connection import get_db
from database.models import Goal, Task, User, MissionResult
from models.schemas import GoalCreate, GoalResponse, GoalDetailResponse, TaskResponse, MissionResultResponse, MissionProgressResponse
from authentication.jwt_handler import get_current_user

router = APIRouter()

from core.event_bus.event_bus import EventBus
from core.event_bus.events import AgentMessageEnvelope
from core.orchestrator.workflow_engine import WorkflowEngine

@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a new high-level goal / mission to the ecosystem."""
    new_goal = Goal(
        user_id=current_user.id,
        title=goal_data.title,
        description=goal_data.description,
        status="created"
    )
    db.add(new_goal)
    await db.flush()

    # Register workflow state in engine
    engine = WorkflowEngine()
    await engine.register_workflow(str(new_goal.id))

    # Publish to event bus to trigger execution DAG
    event_bus = EventBus()
    from core.event_bus.events import MissionEvents
    goal_event = AgentMessageEnvelope(
        source_agent="gateway",
        target_agent="supervisor_agent",
        event_type=MissionEvents.MISSION_CREATED,
        correlation_id=str(new_goal.id),
        payload={
            "goal_title": new_goal.title,
            "goal_description": new_goal.description
        }
    )
    await event_bus.publish("goal.created", goal_event)
    
    await db.commit()
    await db.refresh(new_goal)
    return new_goal

@router.get("/", response_model=List[GoalResponse])
async def list_goals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all goals submitted by the active user (or all goals if admin/developer)."""
    if current_user.role in ["admin", "developer"]:
        result = await db.execute(
            select(Goal)
            .order_by(Goal.created_at.desc())
        )
    else:
        result = await db.execute(
            select(Goal)
            .where(Goal.user_id == current_user.id)
            .order_by(Goal.created_at.desc())
        )
    return result.scalars().all()

from core.orchestrator.response_composer import ResponseComposer

@router.get("/{goal_id}", response_model=GoalDetailResponse)
async def get_goal(
    goal_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve detailed state of a goal/mission."""
    if current_user.role in ["admin", "developer"]:
        result = await db.execute(
            select(Goal)
            .where(Goal.id == goal_id)
        )
    else:
        result = await db.execute(
            select(Goal)
            .where(Goal.id == goal_id, Goal.user_id == current_user.id)
        )
    goal = result.scalars().first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Fetch MissionResult if persisted
    res_stmt = select(MissionResult).where(MissionResult.goal_id == goal.id)
    res_result = await db.execute(res_stmt)
    mission_result_obj = res_result.scalars().first()

    # Calculate friendly progress step
    step_msg, percentage = ResponseComposer.get_progress_message(goal.status)
    progress = MissionProgressResponse(
        goal_id=goal.id,
        status=goal.status.upper(),
        step_message=step_msg,
        progress_percentage=percentage,
        updated_at=goal.updated_at
    )

    # Expose tasks for goal details so user console can render progress & milestones
    tasks_result = await db.execute(
        select(Task)
        .where(Task.goal_id == goal.id)
        .order_by(Task.created_at.asc())
    )
    tasks = tasks_result.scalars().all()

    return GoalDetailResponse(
        goal=GoalResponse.model_validate(goal),
        tasks=[TaskResponse.model_validate(t) for t in tasks] if tasks else None,
        mission_result=MissionResultResponse.model_validate(mission_result_obj) if mission_result_obj else None,
        progress=progress
    )
