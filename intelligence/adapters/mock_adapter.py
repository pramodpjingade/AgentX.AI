import time
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from intelligence.base_adapter import BaseProviderAdapter
from intelligence.response_object import ModelResponse
from intelligence.cost_optimizer import CostOptimizer

class MockAdapter(BaseProviderAdapter):
    """
    Mock Provider Adapter for offline local testing and unit tests.
    Generates high-fidelity simulated responses without leaking internal metadata,
    while correctly formatting code and Markdown blocks.
    """

    def __init__(self):
        super().__init__("mock")

    def is_configured(self) -> bool:
        return True

    def _generate_clean_mock(self, prompt: str, system_instruction: str) -> str:
        p_lower = prompt.lower()
        s_lower = system_instruction.lower()

        # Date & Time queries
        if any(w in p_lower for w in ["what is today's date", "today's date", "current date", "what date is it", "today date"]):
            now = datetime.now()
            return f"📅 Today's date is **{now.strftime('%A, %B %d, %Y')}**."

        if any(w in p_lower for w in ["what time is it", "current time", "what is the time", "tell me the time"]):
            now = datetime.now()
            return f"🕒 The current time is **{now.strftime('%I:%M:%S %p')}**."

        # C code request
        if "c program" in p_lower or "c code" in p_lower or ("c" in p_lower.split() and "code" in p_lower):
            if "add two numbers" in p_lower or "addition" in p_lower or "add" in p_lower:
                return """Here is a complete, well-formatted C program to add two numbers:

```c
#include <stdio.h>

int main() {
    int num1, num2, sum;

    // Prompt user for input
    printf("Enter two integers: ");
    if (scanf("%d %d", &num1, &num2) != 2) {
        printf("Error: Invalid input.\\n");
        return 1;
    }

    // Calculate sum
    sum = num1 + num2;

    // Display the result
    printf("Sum: %d + %d = %d\\n", num1, num2, sum);

    return 0;
}
```

### Explanation:
1. `#include <stdio.h>` imports standard input/output functions.
2. `scanf("%d %d", &num1, &num2)` securely captures the two integers from standard input.
3. `sum = num1 + num2` calculates the sum and prints it formatted to the console."""

        # Python program to reverse a string
        if "reverse a string" in p_lower or ("reverse" in p_lower and "string" in p_lower):
            return """Here is a Python program to reverse a string:

```python
def reverse_string(text: str) -> str:
    \"\"\"Reverses the input string using Python slicing.\"\"\"
    return text[::-1]

# Example Demonstration
if __name__ == "__main__":
    sample_text = "AgentX AI"
    reversed_text = reverse_string(sample_text)
    print(f"Original: {sample_text}")
    print(f"Reversed: {reversed_text}")
```

### Alternative Methods:
- **Using `reversed()` and `join()`:** `''.join(reversed(text))`
- **Using a loop:** Iterating backwards from `len(text) - 1` to `0`."""

        # Research on robotics
        if "robotics" in p_lower:
            return """### Robotics Technology Research & Roadmap

#### 1. Current State of Technology
- **Embodied AI & Foundation Models:** Vision-Language-Action (VLA) models enable generalized manipulation and multimodal reasoning.
- **Humanoid Robotics:** Rapid advancements in electric actuators, dynamic bipedal balancing, and tactile sensing.
- **Autonomous Mobile Robots (AMRs):** Factory automation driven by SLAM algorithms and 3D LiDAR perception.

#### 2. Strategic Roadmap
- **Phase 1 (Months 1–3): Perception & Teleoperation** — High-frequency sensor fusion and teleoperation data collection.
- **Phase 2 (Months 4–6): Policy Training & Simulation** — Reinforcement learning in high-speed physics simulators (Isaac Sim).
- **Phase 3 (Months 7–12): Hardware Deployment** — Real-world zero-shot transfer, tactile manipulation, and safety interlocks."""

        # Check whether a number is prime
        if "prime" in p_lower:
            return """Here is a Python program to check whether a number is prime:

```python
def is_prime(n: int) -> bool:
    \"\"\"Determines if an integer n is prime.\"\"\"
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# Example Usage
if __name__ == "__main__":
    test_numbers = [2, 17, 20, 29, 49]
    for num in test_numbers:
        print(f"{num} is prime: {is_prime(num)}")
```

### Explanation:
- Numbers $\\le 1$ are not prime.
- $2$ and $3$ are the first prime numbers.
- We check divisors up to $\\sqrt{n}$ using the $6k \\pm 1$ optimization for $O(\\sqrt{n})$ efficiency."""

        # Contextual conversation memory check (e.g. favorite color, previous turn facts)
        if "conversation context:" in p_lower or "favorite color" in p_lower:
            if "emerald green" in p_lower:
                return "Based on our earlier conversation, your favorite color is **emerald green**."
            elif "blue" in p_lower:
                return "Based on our earlier conversation, your favorite color is **blue**."

        # General Python code
        if "python" in p_lower and any(w in p_lower for w in ["write", "program", "code", "script"]):
            return """```python
def main():
    print("Hello from AgentX!")

if __name__ == "__main__":
    main()
```"""

        # Explain recursion
        if "recursion" in p_lower:
            return """### Understanding Recursion

**Recursion** is a programming technique where a function calls itself directly or indirectly to solve a problem by breaking it down into smaller, self-similar subproblems.

Every recursive function requires two core components:
1. **Base Case:** A terminating condition that stops recursion and prevents an infinite loop.
2. **Recursive Step:** The logic where the function calls itself with modified arguments moving towards the base case.

---

### Example: Factorial Calculation

The factorial of $n$ ($n!$) is defined as:
- $0! = 1$ (Base Case)
- $n! = n \\times (n - 1)!$ (Recursive Step)

```python
def factorial(n: int) -> int:
    # 1. Base Case: stop when n reaches 0 or 1
    if n <= 1:
        return 1
    
    # 2. Recursive Step: call factorial with (n - 1)
    return n * factorial(n - 1)

# Testing the function
print(f"5! = {factorial(5)}")  # Output: 120
```

### Call Stack Visualization for `factorial(3)`:
- `factorial(3)` calls `3 * factorial(2)`
- `factorial(2)` calls `2 * factorial(1)`
- `factorial(1)` returns `1` (Base case reached)
- Unwinding: `2 * 1 = 2` → `3 * 2 = 6`."""

        # What is Python
        if "what is python" in p_lower or ("python" in p_lower and "what" in p_lower and len(p_lower.split()) < 6):
            return """**Python** is a high-level, interpreted, general-purpose programming language renowned for its clean syntax, readability, and versatile standard library.

### Key Features:
- **Readability:** Clean indentation-based syntax reduces boilerplate code.
- **Interpreted:** Executes line-by-line without requiring ahead-of-time compilation.
- **Dynamically Typed:** Variable types are resolved at runtime.
- **Multi-paradigm:** Supports Object-Oriented, Functional, and Procedural programming styles.
- **Ecosystem:** Powers modern Machine Learning, Data Science, Web Development (FastAPI, Django), and Automation."""

        # What is 2 + 2
        if "2 + 2" in p_lower or "2+2" in p_lower:
            return "2 + 2 = **4**."

        # Master Agent Synthesis
        if "master_agent" in s_lower or "master agent" in s_lower or "synthesize" in p_lower:
            # Extract substantive content from prompt, skipping internal headers
            clean_lines = []
            for line in prompt.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("--- Agent Result") or stripped.startswith("--- Subtask Result"):
                    continue
                if any(stripped.startswith(prefix) for prefix in ["Goal:", "Description:", "Below are", "Synthesize this", "Format with clean"]):
                    continue
                if stripped.startswith("{'status'") or stripped.startswith('{"status"'):
                    continue
                clean_lines.append(stripped)

            body = "\n\n".join(clean_lines).strip()
            if body:
                return body
            else:
                return "The requested mission deliverable has been synthesized and completed successfully."

        # Fallback simulation
        return f"I have processed your request for: **{prompt[:80]}**. Here is the requested output tailored to your specifications."

    async def execute(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> ModelResponse:
        start_time = time.time()
        model_used = model_name or "mock-model"
        await asyncio.sleep(0.05)  # Fast simulated latency

        response_text = self._generate_clean_mock(prompt, system_instruction)

        execution_time = time.time() - start_time
        latency_ms = int(execution_time * 1000)

        prompt_tokens = len(prompt) // 4
        completion_tokens = len(response_text) // 4
        total_tokens = prompt_tokens + completion_tokens
        cost_usd = CostOptimizer.calculate_cost("mock", prompt_tokens, completion_tokens)

        return ModelResponse(
            response_text=response_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            provider="mock",
            model=model_used,
            confidence_score=0.98,
            finish_reason="stop"
        )

    async def stream(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful assistant.",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        clean_text = self._generate_clean_mock(prompt, system_instruction)
        import re
        words = re.findall(r'(\S+\s*)', clean_text)
        if not words:
            yield clean_text
            return

        for i in range(0, len(words), 3):
            yield "".join(words[i:i+3])
            await asyncio.sleep(0.005)
