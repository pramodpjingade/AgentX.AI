import time
from typing import Dict, Any
from loguru import logger
from tools.base_tool import BaseTool, ToolResult

class DocumentGeneratorAdapter(BaseTool):
    """Universal Document & Artifact Generator Tool Adapter for AgentX."""

    def __init__(self):
        super().__init__(
            name="document_generator",
            description="Generates downloadable document artifacts including Markdown, CSV, JSON, and PDF bundles.",
            version="1.2.0",
            capabilities=["document_generator", "pdf_generator", "csv_generator", "markdown_generator"],
            permissions=["document_generator"],
            ttl_seconds=0
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        doc_type = parameters.get("doc_type", "markdown")
        title = parameters.get("title", "Generated_Deliverable")
        content = parameters.get("content", "")

        logger.info(f"DocumentGeneratorAdapter: Generating '{doc_type}' document titled '{title}'")

        artifact = {
            "title": title,
            "doc_type": doc_type,
            "filename": f"{title.lower().replace(' ', '_')}.{doc_type if doc_type != 'markdown' else 'md'}",
            "size_bytes": len(content.encode("utf-8")),
            "content": content
        }

        execution_time = time.time() - start_time
        latency = int(execution_time * 1000)

        return ToolResult(
            status="success",
            success=True,
            data=artifact,
            metadata={"doc_type": doc_type, "title": title},
            latency=latency,
            execution_time=execution_time,
            artifacts=[artifact]
        )
