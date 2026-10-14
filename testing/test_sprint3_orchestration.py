import asyncio
import os
import sys
from uuid import uuid4

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator.graph import orchestrator_graph, AgentXState

async def test_sprint3_orchestrator_flow():
    print("\n==================================================")
    print("RUNNING SPRINT 3 ORCHESTRATION FLOW INTEGRATION TEST")
    print("==================================================")

    # Define initial State Graph variables
    initial_state = {
        "goal_id": str(uuid4()),
        "goal_title": "Build a Simple CSV Data Processing Tool",
        "goal_description": "We need a Python script to read, validate, and summarize CSV sales records.",
        "tasks": [],
        "current_task_index": 0,
        "results": {},
        "next_agent": None,
        "global_context": {},
        "output": "",
        "errors": []
    }

    print("Invoking LangGraph Orchestrator pipeline with initial state...")
    try:
        final_state = await orchestrator_graph.ainvoke(initial_state)
        
        print("\nOrchestrator Execution Completed Successfully!")
        print(f"Goal Title: '{final_state.get('goal_title')}'")
        print(f"Tasks planned: {len(final_state.get('tasks', []))}")
        print("Tasks completed:")
        for idx, task in enumerate(final_state.get("tasks", [])):
            print(f"  - Task {idx+1}: Agent: {task.get('assigned_agent')}, Status: {task.get('status')}")
            
        print("\nFinal Synthesized Output:")
        print(final_state.get("output"))
        
        # Basic assertions
        assert len(final_state.get("tasks", [])) > 0, "Error: Task planner failed to output execution DAG."
        assert final_state.get("output") != "", "Error: Synthesized output is empty."
        print("\nSprint 3 LangGraph Orchestrator transitions verified!")
        
    except Exception as e:
        print(f"Error during LangGraph integration run: {e}")
        raise e

    print("\n==================================================")
    print("SPRINT 3 INTEGRATION TEST: ALL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(test_sprint3_orchestrator_flow())
