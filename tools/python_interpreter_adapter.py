import time
from typing import Dict, Any
from loguru import logger
from tools.base_tool import BaseTool, ToolResult
from tools.code_executor import CodeExecutorTool

class PythonInterpreterAdapter(BaseTool):
    """Universal Python Interpreter Tool Adapter for AgentX."""

    def __init__(self):
        super().__init__(
            name="python_interpreter",
            description="Executes Python code blocks safely inside an isolated subprocess sandbox with timeouts.",
            version="1.2.0",
            capabilities=["python_interpreter", "code_execution", "sandbox_running"],
            permissions=["python_interpreter"],
            ttl_seconds=0  # Never cache code executions
        )
        self.executor = CodeExecutorTool(timeout_seconds=15.0)

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        code = parameters.get("code") or parameters.get("script") or ""

        logger.info("PythonInterpreterAdapter: Running Python script sandbox execution...")

        try:
            res = self.executor.execute_python_code(code)
            execution_time = time.time() - start_time
            latency = int(execution_time * 1000)

            success = res.get("success", False)
            status_str = "success" if success else "failed"

            return ToolResult(
                status=status_str,
                success=success,
                data=res,
                metadata={"returncode": res.get("returncode")},
                latency=latency,
                execution_time=execution_time,
                logs=[f"Subprocess finished with exit code {res.get('returncode')}"],
                errors=[res.get("stderr")] if res.get("stderr") and not success else []
            )
        except Exception as e:
            execution_time = time.time() - start_time
            latency = int(execution_time * 1000)
            logger.error(f"PythonInterpreterAdapter crash: {e}")
            return ToolResult(
                status="failed",
                success=False,
                data=None,
                errors=[str(e)],
                latency=latency,
                execution_time=execution_time
            )
