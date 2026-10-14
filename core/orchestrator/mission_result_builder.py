from typing import Dict, Any, Optional
import uuid
import time
from datetime import datetime
from loguru import logger
from sqlalchemy.future import select

from database.connection import async_session
from database.models import MissionResult, Goal
from core.event_bus.event_bus import EventBus
from core.event_bus.events import AgentMessageEnvelope, MissionEvents

class MissionResultBuilder:
    """
    Mission Result Builder
    Persists the final synthesized AI deliverable into the database as a MissionResult entity.
    Never reconstructs answers from raw task logs.
    """

    @classmethod
    async def build_and_persist(
        cls,
        goal_id: str,
        title: str,
        status: str,
        composed_result: Dict[str, Any],
        execution_time: int = 0,
        error_message: Optional[str] = None
    ) -> Optional[MissionResult]:
        """Constructs and persists a MissionResult database entity."""
        logger.info(f"MissionResultBuilder: Building MissionResult for goal '{goal_id}'")

        goal_uuid = uuid.UUID(goal_id) if isinstance(goal_id, str) else goal_id
        category = composed_result.get("category", "general")
        summary = composed_result.get("summary", f"Mission deliverables for '{title}'.")
        markdown_output = composed_result.get("markdown_output", "")
        structured_output = composed_result.get("structured_output", composed_result.get("deliverable", {}))
        
        # Build artifacts list
        artifacts = []
        if isinstance(structured_output, dict):
            if "files" in structured_output:
                artifacts.extend(structured_output["files"])
            if "actions" in structured_output:
                artifacts.append({"type": "actions", "actions": structured_output["actions"]})

        async with async_session() as db:
            try:
                # Check if MissionResult already exists for this goal
                stmt = select(MissionResult).where(MissionResult.goal_id == goal_uuid)
                res = await db.execute(stmt)
                existing = res.scalars().first()

                if existing:
                    existing.status = status
                    existing.title = title
                    existing.summary = summary
                    existing.structured_output = structured_output
                    existing.markdown_output = markdown_output
                    existing.json_output = composed_result
                    existing.artifacts = artifacts
                    existing.confidence_score = 95
                    existing.execution_time = execution_time
                    existing.error_message = error_message
                    existing.completed_at = datetime.utcnow()
                    mission_res = existing
                else:
                    mission_res = MissionResult(
                        goal_id=goal_uuid,
                        mission_type=category,
                        status=status,
                        title=title,
                        summary=summary,
                        structured_output=structured_output,
                        markdown_output=markdown_output,
                        json_output=composed_result,
                        artifacts=artifacts,
                        confidence_score=95,
                        execution_time=execution_time,
                        error_message=error_message,
                        created_at=datetime.utcnow(),
                        completed_at=datetime.utcnow()
                    )
                    db.add(mission_res)

                # Also update Goal model status
                goal_stmt = select(Goal).where(Goal.id == goal_uuid)
                goal_res = await db.execute(goal_stmt)
                goal_obj = goal_res.scalars().first()
                if goal_obj:
                    goal_obj.status = status.lower()

                await db.commit()
                await db.refresh(mission_res)
                logger.info(f"MissionResultBuilder: Successfully persisted MissionResult {mission_res.id} for goal {goal_id}")

                # Publish MissionResultCreated event to EventBus
                event_bus = EventBus()
                event = AgentMessageEnvelope(
                    source_agent="mission_result_builder",
                    target_agent="gateway",
                    event_type=MissionEvents.MISSION_RESULT_CREATED,
                    correlation_id=str(goal_uuid),
                    payload={
                        "mission_result_id": str(mission_res.id),
                        "goal_id": str(goal_uuid),
                        "mission_type": category,
                        "status": status,
                        "title": title,
                        "summary": summary
                    }
                )
                await event_bus.publish("mission.result_created", event)
                return mission_res

            except Exception as e:
                logger.error(f"MissionResultBuilder: Failed to persist MissionResult for goal {goal_id}: {e}")
                await db.rollback()
                return None
