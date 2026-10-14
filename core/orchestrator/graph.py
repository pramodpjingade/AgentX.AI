from typing import Dict, Any, List, TypedDict, Annotated, Optional
import operator
from langgraph.graph import StateGraph, END
from loguru import logger
import uuid
import json

# Define the state schema shared across all nodes in the graph
class AgentXState(TypedDict):
    goal_id: str
    goal_title: str
    goal_description: str
    tasks: List[Dict[str, Any]]
    current_task_index: int
    results: Dict[str, Any]
    next_agent: Optional[str]
    global_context: Dict[str, Any]
    output: str
    errors: List[str]

# --- Nodes ---

async def planning_node(state: AgentXState) -> Dict[str, Any]:
    """Generates the task execution plan (DAG) using the Planning Agent."""
    logger.info(f"Orchestrator Node [PlanningAgent]: Decomposing goal '{state['goal_title']}'")
    
    from core.task_manager.dag_generator import TaskDAGGenerator
    from database.connection import async_session
    from database.models import Goal, Task
    from sqlalchemy.future import select
    from agents.registry import AgentRegistry
    from core.event_bus.event_bus import EventBus
    from core.event_bus.events import AgentMessageEnvelope, MissionEvents
    
    event_bus = EventBus()
    # Publish MissionStarted and MissionProgress events
    start_event = AgentMessageEnvelope(
        source_agent="orchestrator",
        target_agent="gateway",
        event_type=MissionEvents.MISSION_STARTED,
        correlation_id=state["goal_id"],
        payload={"goal_id": state["goal_id"], "title": state["goal_title"], "status": "PLANNING"}
    )
    await event_bus.publish("mission.started", start_event)

    progress_event = AgentMessageEnvelope(
        source_agent="planning_agent",
        target_agent="gateway",
        event_type=MissionEvents.MISSION_PROGRESS,
        correlation_id=state["goal_id"],
        payload={
            "goal_id": state["goal_id"],
            "status": "PLANNING",
            "step_message": "Planning your mission...",
            "progress_percentage": 25
        }
    )
    await event_bus.publish("mission.progress", progress_event)
    
    # Instantiate the planning agent for records
    registry = AgentRegistry()
    planner_agent = registry.instantiate_agent("planning_agent")
    
    if not state.get("tasks"):
        from agents.model_manager import ModelManager
        manager = ModelManager()
        generator = TaskDAGGenerator()
        tasks = await generator.generate_dag(state["goal_title"], state["goal_description"], manager)
        
        # Save tasks to database and update goal status
        try:
            async with async_session() as db:
                goal_uuid = uuid.UUID(state["goal_id"])
                stmt = select(Goal).where(Goal.id == goal_uuid)
                result = await db.execute(stmt)
                goal = result.scalars().first()
                if goal:
                    goal.status = "executing"
                
                for t in tasks:
                    parent_id = t.get("parent_task_id")
                    if parent_id is not None:
                        if not isinstance(parent_id, uuid.UUID):
                            parent_id = uuid.UUID(str(parent_id))
                    
                    db_task = Task(
                        id=t["id"] if isinstance(t["id"], uuid.UUID) else uuid.UUID(str(t["id"])),
                        goal_id=goal_uuid,
                        assigned_agent=t["assigned_agent"],
                        status=t["status"],
                        input_data=t["input_data"],
                        parent_task_id=parent_id
                    )
                    db.add(db_task)
                
                await db.commit()
        except Exception as e:
            logger.error(f"Orchestrator Node [PlanningAgent]: Failed to persist plan to database: {e}")

        return {
            "tasks": tasks,
            "current_task_index": 0,
            "results": {},
            "errors": []
        }
    return {}

async def router_node(state: AgentXState) -> Dict[str, Any]:
    """Inspects the current task and uses the Router Agent / Supervisor Agent to determine next routing."""
    import asyncio
    from core.orchestrator.workflow_engine import WorkflowEngine
    engine = WorkflowEngine()
    
    while True:
        status = await engine.get_status(state["goal_id"])
        if status == "paused":
            logger.info(f"Orchestrator Node [RouterAgent]: Goal '{state['goal_id']}' is paused. Waiting for resume signal...")
            await asyncio.sleep(1.0)
        elif status == "cancelled":
            logger.info(f"Orchestrator Node [RouterAgent]: Goal '{state['goal_id']}' has been cancelled. Routing to CONSOLIDATION.")
            return {"next_agent": "master_agent_consolidator"}
        else:
            break

    tasks = state.get("tasks", [])
    index = state.get("current_task_index", 0)
    
    if index >= len(tasks):
        logger.info("Orchestrator Node [RouterAgent]: All subtasks completed. Routing to CONSOLIDATION.")
        return {"next_agent": "master_agent_consolidator"}

    from agents.registry import AgentRegistry
    registry = AgentRegistry()
    available_agents = registry.list_agents()

    current_task = tasks[index]
    assigned_agent = current_task.get("assigned_agent", "research_agent")

    # If supervisor specifically recommended an agent for this task
    try:
        supervisor = registry.instantiate_agent("supervisor_agent")
        history = [
            {"task_index": i, "assigned_agent": t.get("assigned_agent"), "status": t.get("status")}
            for i, t in enumerate(tasks)
        ]
        decision = await supervisor.execute({
            "goal": state.get("goal_title", ""),
            "task_history": history
        })
        recommended = decision.get("next_agent")
        if recommended and recommended != "complete" and recommended in available_agents:
            assigned_agent = recommended
    except Exception as e:
        logger.debug(f"RouterNode supervisor check note: {e}")

    if assigned_agent not in available_agents:
        assigned_agent = "research_agent"

    logger.info(f"Orchestrator Node [RouterAgent]: Task {index+1}/{len(tasks)} routed to '{assigned_agent}'")
    return {"next_agent": assigned_agent}

async def agent_execution_node(state: AgentXState) -> Dict[str, Any]:
    """Runs the dynamic agent execution pipeline: Safety -> RAG -> Tool Execution -> Specialized Agent -> Fact Verification."""
    tasks = state.get("tasks", [])
    index = state.get("current_task_index", 0)
    current_task = tasks[index]
    agent_name = state.get("next_agent", "master_agent")
    
    logger.info(f"Orchestrator Node [Pipeline]: Executing task {index+1} with agent '{agent_name}'")
    
    from agents.registry import AgentRegistry
    from database.connection import async_session
    from database.models import Task
    from sqlalchemy.future import select
    import uuid
    
    # Update task status to running in DB
    try:
        async with async_session() as db:
            task_uuid = current_task["id"] if isinstance(current_task["id"], uuid.UUID) else uuid.UUID(str(current_task["id"]))
            stmt = select(Task).where(Task.id == task_uuid)
            result_db = await db.execute(stmt)
            db_task = result_db.scalars().first()
            if db_task:
                db_task.status = "running"
                await db.commit()
    except Exception as e:
        logger.error(f"Orchestrator Node [Pipeline]: Failed to update task to running in DB: {e}")

    registry = AgentRegistry()
    global_context = state.get("global_context", {}).copy()
    
    try:
        # 1. Intent / Safety Guardian check (Governance Layer / Safety Agent)
        logger.info("Orchestrator Node [SafetyAgent]: Auditing task input parameters...")
        safety_agent = registry.instantiate_agent("safety_agent")
        safety_result = await safety_agent.execute({"content": str(current_task.get("input_data", {}))})
        
        # 2. Knowledge Retrieval (RAG Agent)
        logger.info("Orchestrator Node [RAGAgent]: Extracting contextual vectors...")
        rag_agent = registry.instantiate_agent("rag_agent")
        rag_result = await rag_agent.execute({"query": state.get("goal_title", "")})
        global_context["rag_context"] = rag_result.get("result", "")
        
        # 3. Tool Execution Layer check
        logger.info("Orchestrator Node [ToolExecutionAgent]: Verifying tool permission profiles...")
        tool_agent = registry.instantiate_agent("tool_execution_agent")
        tool_result = await tool_agent.execute({"task": str(current_task.get("input_data", {}))})
        
        # Fetch user long-term and short-term memory to build the digital user twin
        from database.connection import async_session
        from database.models import Goal
        from memory.long_term import LongTermMemory
        from sqlalchemy.future import select
        import uuid
        
        try:
            async with async_session() as db:
                goal_uuid = uuid.UUID(state["goal_id"])
                stmt = select(Goal).where(Goal.id == goal_uuid)
                res = await db.execute(stmt)
                goal = res.scalars().first()
                if goal:
                    user_id = goal.user_id
                    memories = await LongTermMemory.get_memories_by_user(db, user_id)
                    global_context["user_memories"] = [m.content for m in memories]
                    global_context["user_preferences"] = [m.content for m in memories if m.memory_type == "preference"]
                    global_context["digital_twin"] = {
                        "user_id": str(user_id),
                        "preferences": [m.content for m in memories if m.memory_type == "preference"],
                        "facts": [m.content for m in memories if m.memory_type == "semantic"]
                    }
        except Exception as mem_err:
            logger.warning(f"Orchestrator Node [agent_execution_node]: Failed loading user memories: {mem_err}")

        # 4. Specialized Agent Execution (Travel, Education, Coding, etc.)
        logger.info(f"Orchestrator Node [Specialized Agent]: Invoking reasoning kernel for '{agent_name}'")
        agent = registry.instantiate_agent(agent_name)
        result = await agent.execute(
            task_input=current_task.get("input_data", {}),
            global_context=global_context
        )
        
        # 5. Fact Verification Layer
        logger.info("Orchestrator Node [FactVerificationAgent]: Testing factual assertions...")
        fact_agent = registry.instantiate_agent("fact_verification_agent")
        fact_result = await fact_agent.execute({
            "content": result.get("result", ""),
            "reference_context": global_context["rag_context"]
        })
        
        # 6. Governance compliance checkpoint
        logger.info("Orchestrator Node [GovernanceLayer]: Verifying policy compliance...")
        governance_agent = registry.instantiate_agent("governance_layer")
        gov_result = await governance_agent.execute({"content": result.get("result", "")})

    except Exception as e:
        logger.error(f"Orchestrator Node [Pipeline]: Execution breakdown on '{agent_name}': {e}")
        result = {
            "status": "failed",
            "result": f"Execution failed on agent '{agent_name}': {e}"
        }
    
    # Save results mapping
    updated_results = state.get("results", {}).copy()
    task_id_str = str(current_task.get("id", uuid.uuid4()))
    updated_results[task_id_str] = result
    
    # Update task status inside list
    updated_tasks = [t.copy() for t in tasks]
    new_status = "completed" if result.get("status") != "failed" else "failed"
    updated_tasks[index]["status"] = new_status
    updated_tasks[index]["output_data"] = result
    
    # Update task status and output_data in DB
    try:
        async with async_session() as db:
            task_uuid = current_task["id"] if isinstance(current_task["id"], uuid.UUID) else uuid.UUID(str(current_task["id"]))
            stmt = select(Task).where(Task.id == task_uuid)
            result_db = await db.execute(stmt)
            db_task = result_db.scalars().first()
            if db_task:
                db_task.status = new_status
                db_task.output_data = result
                await db.commit()
    except Exception as e:
        logger.error(f"Orchestrator Node [Pipeline]: Failed to update task status in DB: {e}")
        
    return {
        "results": updated_results,
        "tasks": updated_tasks
    }

async def evaluation_node(state: AgentXState) -> Dict[str, Any]:
    """Verifies that the executed task matches the quality metrics using the Evaluation Agent."""
    tasks = state.get("tasks", [])
    index = state.get("current_task_index", 0)
    
    logger.info(f"Orchestrator Node [EvaluationAgent]: Auditing task output quality at index {index}")
    
    from agents.registry import AgentRegistry
    registry = AgentRegistry()
    
    try:
        evaluator = registry.instantiate_agent("evaluator_agent")
        current_task = tasks[index]
        task_id_str = str(current_task.get("id"))
        task_result = state.get("results", {}).get(task_id_str, {})
        
        eval_result = await evaluator.execute({
            "output_content": task_result.get("result", ""),
            "reference_context": state.get("global_context", {}).get("rag_context", "")
        })
        
        logger.info(f"Orchestrator Node [EvaluationAgent]: Scorecard resolved. Passed: {eval_result.get('passed')}")
    except Exception as e:
        logger.warning(f"Orchestrator Node [EvaluationAgent]: QA failed to audit task: {e}")

    return {
        "current_task_index": index + 1
    }

async def consolidation_node(state: AgentXState) -> Dict[str, Any]:
    """Invokes the Master Agent to synthesize all outputs into the final operating system response."""
    logger.info("Orchestrator Node [MasterAgent]: Synthesizing operating system final answer...")
    
    from agents.registry import AgentRegistry
    from core.orchestrator.response_composer import ResponseComposer
    from core.orchestrator.mission_result_builder import MissionResultBuilder
    from core.event_bus.event_bus import EventBus
    from core.event_bus.events import AgentMessageEnvelope, MissionEvents
    from database.connection import async_session
    from database.models import Goal
    from sqlalchemy.future import select
    
    event_bus = EventBus()
    # Emit FINALIZING progress event
    progress_event = AgentMessageEnvelope(
        source_agent="master_agent",
        target_agent="gateway",
        event_type=MissionEvents.MISSION_PROGRESS,
        correlation_id=state["goal_id"],
        payload={
            "goal_id": state["goal_id"],
            "status": "FINALIZING",
            "step_message": "Finalizing your personalized deliverable...",
            "progress_percentage": 95
        }
    )
    await event_bus.publish("mission.progress", progress_event)
    
    registry = AgentRegistry()
    master_agent = registry.instantiate_agent("master_agent")
    task_input = {
        "goal_id": state.get("goal_id"),
        "goal_title": state.get("goal_title"),
        "results": state.get("results", {})
    }
    
    execution_result = await master_agent.execute(task_input, state.get("global_context"))
    final_output = execution_result.get("result", "Failed synthesis.")
    
    # Determine final mission status
    from core.orchestrator.workflow_engine import WorkflowEngine
    engine = WorkflowEngine()
    engine_status = await engine.get_status(state["goal_id"])
    
    tasks = state.get("tasks", [])
    any_failed = any(t.get("status") == "failed" for t in tasks)
    any_pending = any(t.get("status") == "pending" for t in tasks)
    
    if engine_status == "cancelled":
        final_status = "CANCELLED"
    elif any_failed or any_pending:
        final_status = "FAILED"
    else:
        final_status = "COMPLETED"

    # Compose structured Mission Result using ResponseComposer
    composed_result = ResponseComposer.compose_mission_result(
        goal_id=state["goal_id"],
        title=state.get("goal_title", "Mission Deliverable"),
        description=state.get("goal_description", ""),
        status=final_status,
        master_output=execution_result,
        tasks=state.get("tasks", [])
    )

    # Persist MissionResult in database using MissionResultBuilder
    await MissionResultBuilder.build_and_persist(
        goal_id=state["goal_id"],
        title=state.get("goal_title", "Mission Deliverable"),
        status=final_status,
        composed_result=composed_result
    )

    # Publish MissionCompleted or MissionFailed event
    event_type = MissionEvents.MISSION_COMPLETED if final_status == "COMPLETED" else MissionEvents.MISSION_FAILED
    complete_event = AgentMessageEnvelope(
        source_agent="master_agent",
        target_agent="gateway",
        event_type=event_type,
        correlation_id=state["goal_id"],
        payload={
            "goal_id": state["goal_id"],
            "status": final_status,
            "deliverable": composed_result.get("deliverable", {})
        }
    )
    await event_bus.publish("mission.completed", complete_event)
        
    return {
        "output": final_output
    }

# --- State Routing Function ---

def route_decision(state: AgentXState) -> str:
    """Decides whether to route to specific agent execution, consolidation, or complete."""
    next_node = state.get("next_agent", "master_agent_consolidator")
    if next_node == "master_agent_consolidator":
        return "consolidation"
    return "agent_executor"


# --- Compile Graph ---

workflow = StateGraph(AgentXState)

# Add nodes to graph
workflow.add_node("planner", planning_node)
workflow.add_node("router", router_node)
workflow.add_node("agent_executor", agent_execution_node)
workflow.add_node("evaluator", evaluation_node)
workflow.add_node("consolidation", consolidation_node)

# Set Entry Point
workflow.set_entry_point("planner")

# Map standard edges
workflow.add_edge("planner", "router")

# Add conditional routing edge from router
workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "agent_executor": "agent_executor",
        "consolidation": "consolidation"
    }
)

# Connect execution to evaluation
workflow.add_edge("agent_executor", "evaluator")
# Loop evaluation back to router to pick up next task
workflow.add_edge("evaluator", "router")

# Connect consolidation to standard END
workflow.add_edge("consolidation", END)

# Compile into a runnable component
orchestrator_graph = workflow.compile()
