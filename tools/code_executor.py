import subprocess
import sys
import tempfile
import os
from typing import Dict, Any
from loguru import logger

class CodeExecutorTool:
    """Executes Python code snippets in a separate subprocess with timeout limits."""
    
    def __init__(self, timeout_seconds: float = 10.0):
        self.timeout = timeout_seconds

    def execute_python_code(self, code: str) -> Dict[str, Any]:
        """Write code to a temporary file and execute it in a subprocess."""
        logger.info("CodeExecutorTool: Initiating execution of Python code block...")
        
        # Create a temporary file to hold the script
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
            f.write(code)
            temp_file_path = f.name
            
        try:
            # Run the script using the active python interpreter executable
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Prepare result dictionary
            success = result.returncode == 0
            logger.info(f"CodeExecutorTool: Completed with returncode {result.returncode}")
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired as e:
            logger.error("CodeExecutorTool: Script execution timed out.")
            return {
                "success": False,
                "stdout": e.stdout or "",
                "stderr": f"Execution Timeout: Script exceeded limit of {self.timeout}s",
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"CodeExecutorTool: Execution crashed: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"System crash during script run: {str(e)}",
                "returncode": -1
            }
        finally:
            # Clean up the temporary script file
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"CodeExecutorTool: Failed to remove temp file {temp_file_path}: {e}")
