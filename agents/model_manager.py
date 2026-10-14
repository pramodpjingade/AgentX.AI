import os
import time
from typing import Optional, Dict, Any
from loguru import logger
from database.connection import async_session
from database.models import ModelRouterLog

# Model Cost Matrix (USD per 1,000,000 tokens)
MODEL_PRICING = {
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "llama3": {"input": 0.0, "output": 0.0},
    "mock": {"input": 0.0, "output": 0.0}
}

MODEL_ALIASES = {
    "FAST_MODEL": {"provider": "openai", "model": "gpt-4o-mini"},
    "REASONING_MODEL": {"provider": "openai", "model": "gpt-4o"},
    "VISION_MODEL": {"provider": "google", "model": "gemini-1.5-flash"},
    "CODING_MODEL": {"provider": "anthropic", "model": "claude-3-5-sonnet-20240620"},
    "LOCAL_MODEL": {"provider": "ollama", "model": "llama3"}
}

class ModelManager:
    """Unified Model Router Interface with complexity analyzer, pricing tracker, and dynamic alias mapping."""
    
    def __init__(self):
        # Load API keys from environment
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def is_configured(self) -> bool:
        """Check if at least one LLM provider is configured."""
        return any([
            self.openai_key and "your-" not in self.openai_key,
            self.anthropic_key and "your-" not in self.anthropic_key,
            self.google_key and "your-" not in self.google_key
        ])

    def analyze_complexity(self, prompt: str) -> str:
        """Analyze query details and choose appropriate model alias."""
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["code", "python", "script", "develop", "function", "lint"]):
            return "CODING_MODEL"
        elif any(w in prompt_lower for w in ["plan", "orchestrate", "complex", "reasoning", "evaluate"]):
            return "REASONING_MODEL"
        elif any(w in prompt_lower for w in ["image", "vision", "picture", "photo"]):
            return "VISION_MODEL"
        return "FAST_MODEL"

    async def generate(
        self, 
        prompt: str, 
        system_instruction: str = "You are a helpful assistant.",
        provider: str = "auto", 
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        task_id: Optional[str] = None
    ) -> str:
        """Routes prompt to Phase 5 IntelligenceRouter gateway and returns response text."""
        from intelligence.router import IntelligenceRouter
        router = IntelligenceRouter()

        response_obj = await router.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            task_id=task_id
        )

        return response_obj.response_text

    async def stream(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        provider: str = "auto",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        """Streams tokens from Phase 5 IntelligenceRouter gateway."""
        from intelligence.router import IntelligenceRouter
        router = IntelligenceRouter()
        async for token in router.stream(
            prompt=prompt,
            system_instruction=system_instruction,
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield token

    async def _log_model_routing(
        self,
        task_id: Optional[str],
        provider: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        latency_ms: int,
        status: str
    ):
        """Persists model metrics database records using an isolated connection context."""
        try:
            async with async_session() as db:
                import uuid
                log_entry = ModelRouterLog(
                    task_id=uuid.UUID(task_id) if task_id else None,
                    provider=provider,
                    model_name=model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost={"usd": cost_usd},
                    latency_ms=latency_ms,
                    status=status
                )
                db.add(log_entry)
                await db.commit()
                logger.info(f"ModelRouterLog: Saved log entry. Latency: {latency_ms}ms, Cost: ${cost_usd:.6f}")
        except Exception as e:
            logger.warning(f"ModelRouterLog: Failed writing logs record: {e}")

    def _generate_mock_response(self, prompt: str, system_instruction: str) -> str:
        """Generates structured diagnostic text to simulate LLM responses locally."""
        prompt_lower = prompt.lower()
        sys_lower = system_instruction.lower()
        
        # Check if this is the Master Agent compiling the final synthesis
        if "master_agent" in sys_lower or "master agent" in sys_lower or "ceo" in sys_lower:
            results_lines = []
            skip_agent = False
            for line in prompt.split("\n"):
                if line.startswith("--- Agent Result"):
                    agent_name = line.split("(")[-1].split(")")[0] if "(" in line and ")" in line else ""
                    if agent_name in ["safety_agent", "intent_agent", "planning_agent", "router_agent", "evaluator_agent", "governance_layer"]:
                        skip_agent = True
                    else:
                        skip_agent = False
                    continue
                if not skip_agent and line.strip() and not line.startswith("{'status'") and not line.startswith('{"id"'):
                    if not line.lower().startswith("synthesize this") and not line.startswith("Goal:") and not line.startswith("Description:"):
                        results_lines.append(line)
            
            cleaned_results = "\n".join(results_lines).strip()
            if cleaned_results:
                return f"### Executive Deliverable\n\n{cleaned_results}\n\n---\n*Synthesized by AgentX AI Operating System.*"
            else:
                goal_title = prompt.split("'")[1] if "'" in prompt else "your request"
                return f"I have processed your request: **{goal_title}**. All multi-agent operations have completed successfully."

        # Check if the prompt is for the supervisor agent routing decision
        if "task history" in prompt_lower or "supervisor" in sys_lower:
            try:
                # Find task history json block in prompt
                if "task history:" in prompt_lower:
                    history_part = prompt.split("Task History:")[1].strip()
                    import json
                    history = json.loads(history_part)
                    
                    # Find first task that is pending
                    next_agent = "complete"
                    for t in history:
                        if t.get("status") == "pending":
                            next_agent = t.get("assigned_agent", "research_agent")
                            break
                    
                    return json.dumps({
                        "next_agent": next_agent,
                        "reason": f"Routing to {next_agent} to execute the next pending subtask."
                    })
            except Exception as e:
                logger.warning(f"Failed to generate mock supervisor response: {e}")
                
            return '{"next_agent": "research_agent", "reason": "Fallback to research agent"}'

        # Check for direct date & time queries (strict phrase check)
        explicit_date_time_phrases = [
            'what is the date', "today's date", 'current date', 'tell me the date', 'what date is today',
            'what is the time', 'what time is it', 'tell me the time', 'current time', 'what day is it', 'what day is today'
        ]
        if any(phrase in prompt_lower for phrase in explicit_date_time_phrases):
            from datetime import datetime
            now = datetime.now()
            return f"📅 Today's date is **{now.strftime('%A, %B %d, %Y')}** and the current time is **{now.strftime('%I:%M:%S %p')}**."

        if "plan" in prompt_lower or "decompose" in prompt_lower or "planning_agent" in sys_lower:
            # Return proper JSON list of tasks depending on prompt keywords
            if any(w in prompt_lower for w in ["date", "time", "clock", "calendar"]):
                return """[
                    {"id": "00000000-0000-0000-0000-000000000001", "assigned_agent": "research_agent", "input_data": {"query": "Retrieve current date and time information"}, "status": "pending", "priority": "HIGH", "estimated_execution_time": 5.0, "estimated_token_usage": 200},
                    {"id": "00000000-0000-0000-0000-000000000002", "assigned_agent": "evaluator_agent", "input_data": {"action": "Verify response formatting"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 5.0, "estimated_token_usage": 100}
                ]"""
            elif "trip" in prompt_lower or "kerala" in prompt_lower or "travel" in prompt_lower:
                return """[
                    {"id": "00000000-0000-0000-0000-000000000001", "assigned_agent": "research_agent", "input_data": {"query": "Search attractions and accommodations in Kerala"}, "status": "pending", "priority": "HIGH", "estimated_execution_time": 30.0, "estimated_token_usage": 1200},
                    {"id": "00000000-0000-0000-0000-000000000002", "assigned_agent": "travel_agent", "input_data": {"query": "Kerala trip itinerary planner"}, "status": "pending", "priority": "HIGH", "estimated_execution_time": 45.0, "estimated_token_usage": 2000},
                    {"id": "00000000-0000-0000-0000-000000000003", "assigned_agent": "fact_verification_agent", "input_data": {"action": "Verify transport rates, ticket costs, and travel advisories for Kerala"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 20.0, "estimated_token_usage": 1000},
                    {"id": "00000000-0000-0000-0000-000000000004", "assigned_agent": "governance_layer", "input_data": {"action": "Check compliance and travel health requirements"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 15.0, "estimated_token_usage": 800}
                ]"""
            elif "basketball" in prompt_lower or "teach" in prompt_lower or "education" in prompt_lower:
                return """[
                    {"id": "00000000-0000-0000-0000-000000000001", "assigned_agent": "research_agent", "input_data": {"query": "Find professional basketball training guides and rules"}, "status": "pending", "priority": "HIGH", "estimated_execution_time": 30.0, "estimated_token_usage": 1200},
                    {"id": "00000000-0000-0000-0000-000000000002", "assigned_agent": "education_agent", "input_data": {"subject": "Basketball skills from scratch"}, "status": "pending", "priority": "HIGH", "estimated_execution_time": 50.0, "estimated_token_usage": 2500},
                    {"id": "00000000-0000-0000-0000-000000000003", "assigned_agent": "fitness_agent", "input_data": {"focus": "Conditioning and physical workouts for basketball"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 30.0, "estimated_token_usage": 1500},
                    {"id": "00000000-0000-0000-0000-000000000004", "assigned_agent": "evaluator_agent", "input_data": {"action": "Assess skill learning benchmarks and testing parameters"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 20.0, "estimated_token_usage": 1000}
                ]"""
            elif "fitness" in prompt_lower or "workout" in prompt_lower or "gym" in prompt_lower:
                return """[
                    {"id": "00000000-0000-0000-0000-000000000001", "assigned_agent": "research_agent", "input_data": {"query": "Gather physiological guidelines for strength training"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 30.0, "estimated_token_usage": 1000},
                    {"id": "00000000-0000-0000-0000-000000000002", "assigned_agent": "fitness_agent", "input_data": {"goal": "Custom workout plan generation"}, "status": "pending", "priority": "HIGH", "estimated_execution_time": 45.0, "estimated_token_usage": 1800},
                    {"id": "00000000-0000-0000-0000-000000000003", "assigned_agent": "evaluator_agent", "input_data": {"action": "Audit physical workload safety limits"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 20.0, "estimated_token_usage": 900}
                ]"""
            elif any(w in prompt_lower for w in ["code", "build", "program", "script", "api", "app", "website", "developer", "function", "repo", "portfolio"]):
                return """[
                    {"id": "00000000-0000-0000-0000-000000000001", "assigned_agent": "research_agent", "input_data": {"query": "Gather best practices for prompt goal"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 30.0, "estimated_token_usage": 1000},
                    {"id": "00000000-0000-0000-0000-000000000002", "assigned_agent": "coding_agent", "input_data": {"instructions": "Generate code or solution"}, "status": "pending", "priority": "HIGH", "estimated_execution_time": 60.0, "estimated_token_usage": 3000},
                    {"id": "00000000-0000-0000-0000-000000000003", "assigned_agent": "evaluator_agent", "input_data": {"action": "Verify execution metrics and formatting"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 20.0, "estimated_token_usage": 1000}
                ]"""
            else:
                # Default general information query decomposition (NO coding_agent!)
                return """[
                    {"id": "00000000-0000-0000-0000-000000000001", "assigned_agent": "research_agent", "input_data": {"query": "Gather background and factual details for user request"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 30.0, "estimated_token_usage": 1000},
                    {"id": "00000000-0000-0000-0000-000000000002", "assigned_agent": "business_agent", "input_data": {"goal": "Synthesize summary response for user query"}, "status": "pending", "priority": "HIGH", "estimated_execution_time": 30.0, "estimated_token_usage": 1500},
                    {"id": "00000000-0000-0000-0000-000000000003", "assigned_agent": "evaluator_agent", "input_data": {"action": "Verify execution formatting"}, "status": "pending", "priority": "NORMAL", "estimated_execution_time": 20.0, "estimated_token_usage": 1000}
                ]"""

        # Specialized Agent Mocks
        if "travel_agent" in sys_lower:
            return """🌴 **AgentX Travel Intelligence: 7-Day Kerala Backwater & Hills Itinerary**

### 📅 **Detailed Route & Plan:**
*   **Day 1-2: Cochin (Historic Gateway)**
    *   *Sightseeing:* Fort Kochi, Chinese Fishing Nets, St. Francis Church, Mattancherry Dutch Palace.
    *   *Experience:* Traditional Kathakali dance performance in the evening.
*   **Day 3-4: Munnar (Breathtaking Tea Highlands)**
    *   *Sightseeing:* Eravikulam National Park (home to Nilgiri Tahr), Tea Museum, Mattupetty Dam.
    *   *Experience:* Trekking through organic tea plantations.
*   **Day 5: Thekkady (Wildlife Sanctuary)**
    *   *Sightseeing:* Periyar Tiger Reserve.
    *   *Experience:* Boat safari on Lake Periyar, elephant transit camp, and spice estate tour.
*   **Day 6: Alleppey (The Venice of the East)**
    *   *Experience:* Private luxury *Kettuvallam* houseboat cruise. Sail through pristine backwaters, enjoy local Karimeen fish curry, and watch village life.
*   **Day 7: Varkala (Cliff Beaches & Departure)**
    *   *Sightseeing:* Varkala cliffside walks, Janardhana Swami Temple, beach sunset.
    *   *Departure:* Drive to Trivandrum International Airport (TRV).

### 💰 **Estimated Budget & Logistics:**
*   **Budget Category:** Comfort (4-star hotels & houseboats): ~$650 / ₹54,000 per person.
*   **Transport:** Dedicated air-conditioned private vehicle and local English/Hindi-speaking driver.
*   **Best Time to Visit:** October to March for ideal pleasant weather."""

        elif "education_agent" in sys_lower:
            return """🏀 **AgentX Education Academy: Comprehensive Basketball Training Syllabus**

### 🎯 **Course Objective:**
Decompose the game of basketball into progressive learning modules suitable for beginners to master fundamental skills.

### 📚 **Module 1: Dribbling & Ball Handling (Weeks 1-2)**
*   **Key Concepts:** Finger-tip control, low center of gravity, pocketing the ball.
*   **Drills:**
    1.  *Stationary Dribbling:* 100 right hand, 100 left hand (knee height).
    2.  *Crossovers:* 50 reps maintaining low stance.
    3.  *Figure 8:* Dribbling in and out around legs.

### 📚 **Module 2: Shooting Form & Mechanics (Weeks 3-4)**
*   **Key Concepts:** The **B.E.E.F.** principal:
    *   **B**alance: Feet shoulder-width apart, toes pointing to the basket.
    *   **E**lbow: Kept tucked in, forming an L-shape.
    *   **E**yes: Locked on the front of the rim.
    *   **F**ollow-through: Wrist floppy ("duck neck") pointing to target.
*   **Drills:** Form shooting from 3 feet away without using backboard (50 makes daily).

### 📚 **Module 3: Defensive Stance & Footwork (Weeks 5-6)**
*   **Key Concepts:** Athletic sliding stance, denial position, closeouts.
*   **Drills:** Defensive slides from sideline to sideline (4 sets of 45 seconds).

### 📚 **Module 4: Team Play & Rules (Weeks 7-8)**
*   **Key Concepts:** Violations (traveling, double dribble, 3-seconds), pick-and-roll theory, screening, and floor spacing."""

        elif "fitness_agent" in sys_lower:
            return """🏋️‍♂️ **AgentX Fitness Optimizer: Conditioning & Athletic Workout Guide**

### 🏃 **Warm-up Routine (10 minutes):**
*   Jumping jacks: 3 sets of 30 seconds.
*   High knees & butt kicks: 2 sets of 45 seconds.
*   Arm circles and leg swings: 10 reps each.

### ⚡ **Core Strength Plan (Perform 3 days/week):**
1.  **Bodyweight Squats:** 3 sets of 15 reps (focused on depth and knee tracking).
2.  **Push-ups (Standard/Incline):** 3 sets of 10-12 reps (core locked).
3.  **Reverse Lunges:** 3 sets of 10 reps per leg.
4.  **Plank Hold:** 3 sets of 45-60 seconds.

### 💨 **Cardiovascular & Agility Drills (2 days/week):**
*   **Suicide Runs:** Sprints at 10m, 20m, 30m distances. 5 repetitions.
*   **Jump Rope:** 3 sets of 2 minutes continuous jumping.

### 💧 **Hydration & Recovery:**
*   Drink 3.5 liters of water daily. Focus on 8 hours of quality sleep for muscle recovery."""

        elif "coding_agent" in sys_lower:
            return """```python
# AgentX Coding Core: FastAPI REST Application Template
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="AgentX Dynamic REST API")

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

db: List[Item] = []

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    for i in db:
        if i.id == item.id:
            raise HTTPException(status_code=400, detail="Item already exists")
    db.append(item)
    return item

@app.get("/items/", response_model=List[Item])
def get_all_items():
    return db

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
```"""

        elif "research_agent" in sys_lower:
            if any(w in prompt_lower for w in ["date", "time", "clock", "today", "calendar"]):
                from datetime import datetime
                now = datetime.now()
                return f"📅 Today's date is **{now.strftime('%A, %B %d, %Y')}** and the current time is **{now.strftime('%I:%M:%S %p')}**."
            return """🔍 **AgentX Web Intelligence: Reference Compilation**

### 📊 **Primary Findings Summary:**
A structured sweep of current web databases, public forums, and academic indexing services shows high interest in these parameters.

### 🔗 **Citations & Credible Sources:**
1.  **National Tourism Portal (2026):** Verified boarding requirements, peak seasonal timings, and eco-tourism guidelines.
2.  **Sports Medicine & Education Association (2025):** Standard training guidelines, injury prevention protocols, and developmental training structures.
3.  **W3C Technical Architecture (2026):** Rest API design best practices, JSON schema structures, and routing standards.

### 🗒️ **Fact Extraction Table:**
*   *Kerala Travel:* Current houseboats operate with standard safety certificates. Best months: Nov-Feb.
*   *Basketball:* Proper shooting release angle should be around 45 to 52 degrees.
*   *REST API:* Standard status codes should be HTTP 201 for Created, HTTP 200 for OK."""

        elif "fact_verification_agent" in sys_lower:
            return """🛡️ **AgentX Fact Verification Audit: Success**

*   **Fact Checking Score:** 100% Grounded.
*   **Verification Logs:**
    *   Checked Kerala transport rates: Confirmed taxi fares align with standard state tourist pricing.
    *   Checked training drills: Confirmed drills align with official youth basketball curriculum guidelines.
    *   Hallucination check: 0% ungrounded claims detected.
*   **Status:** APPROVED for Master synthesis."""

        elif "evaluator_agent" in sys_lower:
            return """📊 **AgentX Quality Assurance scorecard**

*   **Grounding Metric:** 0.96 / 1.00
*   **Factual Accuracy Index:** 0.98 / 1.00
*   **Formatting Check:** Valid Markdown syntax and correct indentation.
*   **Evaluation Status:** PASS (Output satisfies target objectives)."""

        elif "governance_layer" in sys_lower:
            return """⚖️ **AgentX Governance & Compliance Audit**

*   **PII Check:** Passed. No emails, phone numbers, or passwords leaked.
*   **Safety Scan:** Passed. No prompt injection attempts or harmful commands found.
*   **Compliance:** Approved for local and enterprise deployment. Data storage complies with default security schemas."""

        elif "rag_agent" in sys_lower:
            return """📚 **AgentX RAG Context Retracted from Vector DB**

*   *Doc Segment 1:* "Kerala offers diverse attractions. Munnar is situated at 1,600m above sea level..." (Score: 0.89)
*   *Doc Segment 2:* "A proper basketball shot is initiated by bending the knees to generate power..." (Score: 0.85)"""

        elif "tool_execution_agent" in sys_lower:
            return """⚙️ **AgentX Tool Execution Layer Logs**

*   **Tool:** WebSearch (Google Search API)
    *   *Parameters:* {"q": "best places in Kerala"}
    *   *Result:* Loaded 10 organic result packets.
*   **Tool:** CodeSandbox Interpreter
    *   *Parameters:* {"language": "python", "code": "print('Compiled')"}
    *   *Result:* "Compiled" (Status: OK, Exit code: 0)"""

        else:
            return f"This is a simulated model output. Prompt was: '{prompt[:50]}...'"

