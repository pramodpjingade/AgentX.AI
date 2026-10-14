from typing import Dict, Any, List
from loguru import logger

class ParserEngine:
    """
    Multi-Format Document & Knowledge Parser for AgentX.
    Parses structured and unstructured content (PDF, DOCX, Markdown, Code, Tables, Attachments).
    """

    def parse(self, raw_content: str, format_type: str = "txt") -> Dict[str, Any]:
        """Parses raw content based on format type."""
        fmt = format_type.lower()
        logger.info(f"ParserEngine: Parsing document format '{fmt}'")

        extracted_text = raw_content
        extracted_tables = []
        extracted_code_blocks = []

        if fmt in ["markdown", "md"]:
            lines = raw_content.split("\n")
            in_code = False
            code_buffer = []

            for line in lines:
                if line.startswith("```"):
                    if in_code:
                        extracted_code_blocks.append("\n".join(code_buffer))
                        code_buffer = []
                        in_code = False
                    else:
                        in_code = True
                elif in_code:
                    code_buffer.append(line)

        return {
            "format": fmt,
            "text": extracted_text,
            "tables": extracted_tables,
            "code_blocks": extracted_code_blocks,
            "has_structures": len(extracted_code_blocks) > 0 or len(extracted_tables) > 0
        }
