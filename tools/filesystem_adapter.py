import time
from typing import Dict, Any
from loguru import logger
from tools.base_tool import BaseTool, ToolResult
from tools.file_processor import FileProcessorTool

class FileSystemAdapter(BaseTool):
    """Universal FileSystem Tool Adapter for AgentX."""

    def __init__(self):
        super().__init__(
            name="filesystem",
            description="Reads, writes, and lists workspace directory files safely with path traversal protection.",
            version="1.2.0",
            capabilities=["filesystem", "read_file", "write_file", "list_directory"],
            permissions=["read_file"],
            ttl_seconds=0
        )
        self.processor = FileProcessorTool()

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        action = parameters.get("action") or parameters.get("operation") or "read"
        filepath = parameters.get("filepath") or parameters.get("path") or "."
        content = parameters.get("content", "")

        logger.info(f"FileSystemAdapter: Executing action '{action}' on path '{filepath}'")

        try:
            if action in ["read", "read_file"]:
                data = self.processor.read_file(filepath)
            elif action in ["write", "write_file"]:
                data = self.processor.write_file(filepath, content)
            elif action in ["list", "list_directory"]:
                data = self.processor.list_directory(filepath)
            else:
                data = self.processor.read_file(filepath)

            execution_time = time.time() - start_time
            latency = int(execution_time * 1000)

            return ToolResult(
                status="success",
                success=True,
                data=data,
                metadata={"action": action, "filepath": filepath},
                latency=latency,
                execution_time=execution_time,
                artifacts=[{"type": "file", "path": filepath}] if action in ["write", "write_file"] else []
            )
        except Exception as e:
            execution_time = time.time() - start_time
            latency = int(execution_time * 1000)
            logger.error(f"FileSystemAdapter error: {e}")
            return ToolResult(
                status="failed",
                success=False,
                data=None,
                errors=[str(e)],
                latency=latency,
                execution_time=execution_time
            )
