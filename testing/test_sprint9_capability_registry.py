import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.registry import AgentRegistry

def test_sprint9_capability_discovery():
    print("\n==================================================")
    print("RUNNING SPRINT 9 CAPABILITY REGISTRY INTEGRATION TEST")
    print("==================================================")

    # 1. Instantiate Registry
    print("[Step 1] Initializing AgentRegistry singleton...")
    registry = AgentRegistry()

    # 2. Query for capability 'web_search'
    print("\n[Step 2] Querying registry for agents supporting capability 'web_search'...")
    agents = registry.find_agents_by_capability("web_search")
    print(f"Matching agents found: {agents}")
    assert "research_agent" in agents, "Error: Expected 'research_agent' to match capability 'web_search'."

    # 3. Query for capability 'code_generation'
    print("\n[Step 3] Querying registry for agents supporting capability 'code_generation'...")
    agents = registry.find_agents_by_capability("code_generation")
    print(f"Matching agents found: {agents}")
    assert "coding_agent" in agents, "Error: Expected 'coding_agent' to match capability 'code_generation'."

    print("\nCapability registry lookups successfully validated!")

    print("\n==================================================")
    print("SPRINT 9 INTEGRATION TEST: ALL TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_sprint9_capability_discovery()
