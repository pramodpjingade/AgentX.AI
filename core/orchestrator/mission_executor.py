import asyncio
import time
import uuid
from typing import Dict, Any, Optional, List
from loguru import logger
from sqlalchemy.future import select

from database.connection import async_session
from database.models import Goal, MissionResult
from core.orchestrator.mission_context import MissionContext
from core.orchestrator.response_composer import ResponseComposer
from core.orchestrator.mission_result_builder import MissionResultBuilder
from core.event_bus.event_bus import EventBus
from core.event_bus.events import AgentMessageEnvelope, MissionEvents
from agents.registry import AgentRegistry

class MissionExecutor:
    """
    Central AI Mission Execution Engine for AgentX (Phase 2 Multi-Agent Framework).
    Orchestrates the full multi-agent lifecycle:
    User Goal -> MissionContext -> Supervisor -> Planner -> Router -> Parallel Specialized Agents -> Evaluation -> Master Agent -> MissionResult.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MissionExecutor, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.registry = AgentRegistry()
        self.event_bus = EventBus()
        self._initialized = True
        logger.info("MissionExecutor: Central AI Mission Execution Engine initialized.")

    async def execute_parallel_agents(self, agent_names: List[str], context: MissionContext) -> MissionContext:
        """Executes independent specialized agents simultaneously using asyncio.gather()."""
        logger.info(f"MissionExecutor: Launching simultaneous parallel execution for agents: {agent_names}")
        async_tasks = []
        for name in agent_names:
            try:
                agent = self.registry.instantiate_agent(name)
                async_tasks.append(agent.execute_context(context))
            except Exception as e:
                logger.warning(f"MissionExecutor: Could not instantiate agent '{name}' for parallel run: {e}")

        if async_tasks:
            results = await asyncio.gather(*async_tasks, return_exceptions=True)
            for name, res in zip(agent_names, results):
                if isinstance(res, Exception):
                    logger.error(f"MissionExecutor: Parallel agent '{name}' failed with exception: {res}")
                    context.add_error(f"Parallel execution error in '{name}': {res}")
        return context

    async def execute_mission(self, goal_id: str) -> Optional[MissionResult]:
        """
        Executes a complete AI mission lifecycle for the specified goal ID.
        """
        start_time = time.time()
        logger.info(f"MissionExecutor: Commencing mission execution pipeline for goal '{goal_id}'")

        goal_uuid = uuid.UUID(goal_id) if isinstance(goal_id, str) else goal_id

        # 1. Load Goal from Database
        async with async_session() as db:
            stmt = select(Goal).where(Goal.id == goal_uuid)
            res = await db.execute(stmt)
            goal_obj = res.scalars().first()
            if not goal_obj:
                logger.error(f"MissionExecutor: Goal ID '{goal_id}' not found in database.")
                return None

            goal_title = goal_obj.title
            goal_description = goal_obj.description or ""
            user_id = str(goal_obj.user_id) if goal_obj.user_id else None

        # 2. Create MissionContext & Build Initial State
        context = MissionContext(
            goal_id=str(goal_uuid),
            user_id=user_id,
            title=goal_title,
            description=goal_description,
            current_status="CREATED"
        )
        context.mission_type = ResponseComposer.classify_category(goal_title, goal_description)

        # Publish MissionCreated and MissionStarted events
        await self.event_bus.publish(
            "mission.created",
            AgentMessageEnvelope(
                source_agent="mission_executor",
                target_agent="gateway",
                event_type=MissionEvents.MISSION_CREATED,
                correlation_id=str(goal_uuid),
                payload={"goal_id": str(goal_uuid), "title": goal_title, "status": "CREATED"}
            )
        )

        context.update_status("STARTED", progress_pct=10)
        await self.event_bus.publish(
            "mission.started",
            AgentMessageEnvelope(
                source_agent="mission_executor",
                target_agent="gateway",
                event_type=MissionEvents.MISSION_STARTED,
                correlation_id=str(goal_uuid),
                payload={"goal_id": str(goal_uuid), "title": goal_title, "status": "STARTED"}
            )
        )

        # 3. Build Cognitive Memory Context & Digital Twin Profile
        try:
            from memory.memory_manager import MemoryManager
            mem_manager = MemoryManager()
            built_context = await mem_manager.build_mission_context(user_id, goal_title)
            context.memory.update(built_context)
            context.knowledge["triples"] = built_context.get("knowledge_graph_triples", "")
            
            # Enterprise Hybrid Knowledge Platform Retrieval
            from knowledge.platform import KnowledgePlatform
            kp = KnowledgePlatform()
            kp_docs = await kp.retrieve_knowledge(goal_title, user_id=user_id)
            context.memory["knowledge_platform_docs"] = [d.get("content", "") for d in kp_docs]

            # Load RAG Context via rag_agent
            rag_agent = self.registry.instantiate_agent("rag_agent")
            rag_result = await rag_agent.execute({"query": goal_title})
            context.memory["rag_context"] = rag_result.get("result", "")
        except Exception as e:
            logger.warning(f"MissionExecutor: MemoryManager / KnowledgePlatform context loading note: {e}")

        # 4. Call Supervisor Agent (Intent & Execution Strategy)
        context.update_status("PLANNING", progress_pct=20)
        await self.event_bus.publish(
            "mission.planning",
            AgentMessageEnvelope(
                source_agent="supervisor_agent",
                target_agent="gateway",
                event_type=MissionEvents.MISSION_PLANNING,
                correlation_id=str(goal_uuid),
                payload={
                    "goal_id": str(goal_uuid),
                    "status": "PLANNING",
                    "step_message": "Analyzing user intent & crafting mission execution strategy...",
                    "progress_percentage": 20
                }
            )
        )

        try:
            supervisor = self.registry.instantiate_agent("supervisor_agent")
            await supervisor.execute_context(context)
        except Exception as e:
            logger.warning(f"MissionExecutor: Supervisor agent execution warning: {e}")

        # 5. Call Planner Agent (Goal Decomposition & DAG Tasks)
        try:
            planner = self.registry.instantiate_agent("planning_agent")
            await planner.execute_context(context)
        except Exception as e:
            logger.warning(f"MissionExecutor: Planner agent execution warning: {e}")

        # 6. Call Router Agent (Dynamic Specialized Agent Selection)
        context.update_status("EXECUTING", progress_pct=40)
        await self.event_bus.publish(
            "mission.executing",
            AgentMessageEnvelope(
                source_agent="router_agent",
                target_agent="gateway",
                event_type=MissionEvents.MISSION_EXECUTING,
                correlation_id=str(goal_uuid),
                payload={
                    "goal_id": str(goal_uuid),
                    "status": "EXECUTING",
                    "step_message": "Routing subtasks to specialized AI agents...",
                    "progress_percentage": 40
                }
            )
        )

        recommended_agents = []
        try:
            router = self.registry.instantiate_agent("router_agent")
            await router.execute_context(context)
            router_out = context.agent_outputs.get("router_agent", {})
            recommended_agents = router_out.get("recommended_agents", [])
        except Exception as e:
            logger.warning(f"MissionExecutor: Router agent execution warning: {e}")

        # 7. Parallel Execution of Independent Specialized Agents
        if recommended_agents:
            # Filter out core infrastructure agents from parallel domain execution
            domain_agents = [a for a in recommended_agents if a not in ["master_agent", "supervisor_agent", "evaluator_agent", "planning_agent", "router_agent"]]
            if domain_agents:
                await self.execute_parallel_agents(domain_agents, context)

        # Execute LangGraph pipeline for remaining task dependencies
        from core.orchestrator.graph import orchestrator_graph
        initial_state = {
            "goal_id": str(goal_uuid),
            "goal_title": goal_title,
            "goal_description": goal_description,
            "tasks": context.tasks,
            "current_task_index": 0,
            "results": context.agent_outputs,
            "next_agent": None,
            "global_context": context.memory,
            "output": "",
            "errors": context.errors
        }

        try:
            final_state = await orchestrator_graph.ainvoke(initial_state)
            if final_state.get("tasks"):
                context.tasks = final_state["tasks"]
            context.agent_outputs.update(final_state.get("results", {}))
            synthesized_markdown = final_state.get("output", "")
        except Exception as e:
            logger.error(f"MissionExecutor: Graph pipeline execution failure: {e}")
            context.add_error(str(e))
            synthesized_markdown = f"Execution halted due to error: {e}"

        # 8. Run Evaluation Agent & Autonomous Reasoning Engine
        context.update_status("EVALUATING", progress_pct=85)
        await self.event_bus.publish(
            "mission.evaluating",
            AgentMessageEnvelope(
                source_agent="evaluator_agent",
                target_agent="gateway",
                event_type=MissionEvents.MISSION_EVALUATING,
                correlation_id=str(goal_uuid),
                payload={
                    "goal_id": str(goal_uuid),
                    "status": "EVALUATING",
                    "step_message": "Auditing quality, self-reflecting, and verifying completeness...",
                    "progress_percentage": 85
                }
            )
        )

        try:
            from reasoning.engine import ReasoningEngine
            reasoning_engine = ReasoningEngine()
            await reasoning_engine.process_mission_cognition(context)

            evaluator = self.registry.instantiate_agent("evaluator_agent")
            await evaluator.execute_context(context)
        except Exception as e:
            logger.warning(f"MissionExecutor: Reasoning/Evaluation agent note: {e}")

        # 9. Run Master Agent (Master Agent is the ONLY component writing final response)
        context.update_status("FINALIZING", progress_pct=95)
        await self.event_bus.publish(
            "mission.finalizing",
            AgentMessageEnvelope(
                source_agent="master_agent",
                target_agent="gateway",
                event_type=MissionEvents.MISSION_FINALIZING,
                correlation_id=str(goal_uuid),
                payload={
                    "goal_id": str(goal_uuid),
                    "status": "FINALIZING",
                    "step_message": "Finalizing your mission deliverable...",
                    "progress_percentage": 95
                }
            )
        )

        master_agent = self.registry.instantiate_agent("master_agent")
        await master_agent.execute_context(context)
        master_output = context.agent_outputs.get("master_agent", {})

        # 10. Generate Final Deliverable via ResponseComposer
        composed_result = ResponseComposer.compose_mission_result(
            goal_id=str(goal_uuid),
            title=goal_title,
            description=goal_description,
            status="COMPLETED",
            master_output=master_output,
            tasks=context.tasks
        )

        execution_duration = int(time.time() - start_time)

        # 11. Store Mission Result in Database
        mission_result = await MissionResultBuilder.build_and_persist(
            goal_id=str(goal_uuid),
            title=goal_title,
            status="COMPLETED",
            composed_result=composed_result,
            execution_time=execution_duration
        )

        # 12. Publish MissionCompleted and WorkflowCompleted Events
        context.update_status("COMPLETED", progress_pct=100)
        await self.event_bus.publish(
            "mission.completed",
            AgentMessageEnvelope(
                source_agent="mission_executor",
                target_agent="gateway",
                event_type=MissionEvents.MISSION_COMPLETED,
                correlation_id=str(goal_uuid),
                payload={
                    "goal_id": str(goal_uuid),
                    "status": "COMPLETED",
                    "mission_type": context.mission_type,
                    "deliverable": composed_result.get("deliverable", {})
                }
            )
        )
        await self.event_bus.publish(
            "workflow.completed",
            AgentMessageEnvelope(
                source_agent="mission_executor",
                target_agent="gateway",
                event_type="WorkflowCompleted",
                correlation_id=str(goal_uuid),
                payload={
                    "goal_id": str(goal_uuid),
                    "status": "COMPLETED",
                    "output": str(composed_result.get("deliverable", {}).get("summary", "Mission completed successfully"))
                }
            )
        )

        logger.info(f"MissionExecutor: Mission execution complete for goal '{goal_id}' in {execution_duration}s")
        return mission_result
