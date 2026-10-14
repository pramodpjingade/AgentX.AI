import asyncio
import sys
import os

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator.graph import orchestrator_graph

async def test_run():
    print("Initializing test run on LangGraph Orchestrator...")
    
    # Configure initial state input
    inputs = {
        "goal_id": "00000000-0000-0000-0000-000000000001",
        "goal_title": "Build a weather forecast site",
        "goal_description": "Create a coding application that scrapes weather info and presents it in python code.",
        "tasks": [],
        "current_task_index": 0,
        "results": {},
        "next_agent": None,
        "global_context": {},
        "output": "",
        "errors": []
    }
    
    print("\nStarting execution graph...\n")
    
    # Run the graph and print state transitions
    async for event in orchestrator_graph.astream(inputs):
        for node_name, state_update in event.items():
            print(f"--- Completed Node: '{node_name}' ---")
            if "tasks" in state_update:
                print(f"Tasks Updated. Current Index: {state_update.get('current_task_index')}")
                for idx, t in enumerate(state_update["tasks"]):
                    print(f"  Task {idx+1}: {t['assigned_agent']} - Status: {t['status']}")
            if "next_agent" in state_update:
                print(f"Next Router Routing: '{state_update['next_agent']}'")
            print("-" * 40)
            
    print("\nLangGraph Orchestrator Execution finished successfully!")

if __name__ == "__main__":
    asyncio.run(test_run())
