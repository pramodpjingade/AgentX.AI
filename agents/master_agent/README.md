# Master Agent (CEO)

## Role & Description
The Master Agent functions as the Chief Executive Officer of the AgentX Multi-Agent Ecosystem. It sits directly under the LangGraph Core Orchestrator. 

Its primary responsibilities are:
1. Receiving user goals from the API layer.
2. Directing task evaluation and results consolidation.
3. Synthesizing subtask outputs (e.g. from Research, Coding, and Security agents) into a unified and polished final response.

## Files
- `agent.py`: Executes task consolidation and synthesis.
- `config.py`: Configuration settings, defaults, temperature configurations.
- `prompts.py`: System instructions and planning/decomposition templates.
- `tools.py`: Helper tools.
- `memory.py`: Local episodic execution history logs.
