import asyncio
from loguru import logger
from core.event_bus.event_bus import EventBus
from core.event_bus.events import AgentMessageEnvelope
from core.orchestrator.graph import orchestrator_graph

class OrchestratorEventWorker:
    """Listens to stream queues and routes messages to core LangGraph processes."""
    
    def __init__(self):
        self.event_bus = EventBus()
        
    async def start(self):
        """Bind topic listeners to the active event loop."""
        logger.info("OrchestratorEventWorker: Bootstrapping subscriber listeners...")
        await self.event_bus.subscribe("goal.created", self.handle_goal_created)
        await self.event_bus.subscribe("task.completed", self.handle_task_completed)

    async def handle_goal_created(self, event: AgentMessageEnvelope):
        """Triggers AI Mission Execution Engine on receipt of goal created event."""
        logger.info(f"OrchestratorEventWorker: Delegating goal creation event {event.event_id} (Goal ID: {event.correlation_id}) to MissionExecutor...")
        
        from core.orchestrator.mission_executor import MissionExecutor
        executor = MissionExecutor()

        try:
            mission_result = await executor.execute_mission(event.correlation_id)
            if mission_result:
                logger.info(f"OrchestratorEventWorker: Mission execution succeeded for goal '{event.correlation_id}'. MissionResult ID: {mission_result.id}")
            else:
                logger.warning(f"OrchestratorEventWorker: Mission execution returned no result for goal '{event.correlation_id}'.")
        except Exception as e:
            logger.error(f"OrchestratorEventWorker: Mission execution failure for goal '{event.correlation_id}': {e}")
            from database.connection import async_session
            from database.models import Goal
            from core.event_bus.events import MissionEvents
            from sqlalchemy.future import select
            import uuid
            try:
                async with async_session() as db:
                    stmt = select(Goal).where(Goal.id == uuid.UUID(event.correlation_id))
                    res = await db.execute(stmt)
                    goal = res.scalars().first()
                    if goal:
                        goal.status = "failed"
                        await db.commit()

                # Emit MissionFailed event
                fail_event = AgentMessageEnvelope(
                    source_agent="orchestrator",
                    target_agent="gateway",
                    event_type=MissionEvents.MISSION_FAILED,
                    correlation_id=event.correlation_id,
                    payload={"goal_id": event.correlation_id, "status": "FAILED", "error": str(e)}
                )
                await self.event_bus.publish("mission.failed", fail_event)
            except Exception as db_err:
                logger.error(f"OrchestratorEventWorker: Failed to mark goal as failed in DB: {db_err}")

    async def handle_task_completed(self, event: AgentMessageEnvelope):
        """Processes task-level callback payloads."""
        logger.info(f"OrchestratorEventWorker: Task callback resolved for correlation ID {event.correlation_id}")
