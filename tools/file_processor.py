import os
from typing import List, Optional
from loguru import logger

class FileProcessorTool:
    """Safe workspace file utilities."""
    
    def __init__(self, allowed_root: str = r"d:\AgentX.AI"):
        self.allowed_root = os.path.abspath(allowed_root)

    def _resolve_safe_path(self, filepath: str) -> str:
        """Resolve and verify path limits to stay inside workspace."""
        absolute_path = os.path.abspath(os.path.join(self.allowed_root, filepath))
        if not absolute_path.startswith(self.allowed_root):
            raise PermissionError(f"Path traversal detected! Access denied outside workspace: {filepath}")
        return absolute_path

    def read_file(self, filepath: str) -> str:
        """Read content from a workspace file."""
        safe_path = self._resolve_safe_path(filepath)
        logger.info(f"FileProcessorTool: Reading file '{safe_path}'")
        
        if not os.path.exists(safe_path):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, filepath: str, content: str) -> bool:
        """Write content to a workspace file, creating directories if missing."""
        safe_path = self._resolve_safe_path(filepath)
        logger.info(f"FileProcessorTool: Writing to file '{safe_path}'")
        
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    def list_directory(self, dirpath: str = ".") -> List[str]:
        """List contents of a directory in the workspace."""
        safe_path = self._resolve_safe_path(dirpath)
        logger.info(f"FileProcessorTool: Listing directory '{safe_path}'")
        
        if not os.path.exists(safe_path):
            raise FileNotFoundError(f"Directory not found: {dirpath}")
            
        return os.listdir(safe_path)
