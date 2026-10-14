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

    DANGEROUS_PATTERNS = [
        "os.system",
        "subprocess",
        "shutil.rmtree",
        "shutil.move",
        ".env",
        "agentx.db",
        "__import__('os').system",
        "__import__('subprocess')",
        "eval(",
        "exec("
    ]

    def _is_safe(self, code: str) -> tuple[bool, str]:
        """Validates code for dangerous system operations or secret leakage."""
        code_lower = code.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in code_lower:
                return False, f"Execution Blocked: Unsafe pattern '{pattern}' detected. Arbitrary system operations and secret access are prohibited."
        return True, ""

    def execute_python_code(self, code: str) -> Dict[str, Any]:
        """Executes Python code in an isolated subprocess with sanitized environment and timeout."""
        logger.info("CodeExecutorTool: Initiating execution of Python code block...")

        # 1. Safety audit
        is_safe, reason = self._is_safe(code)
        if not is_safe:
            logger.warning(f"CodeExecutorTool: {reason}")
            return {
                "success": False,
                "stdout": "",
                "stderr": reason,
                "returncode": -1,
                "sandboxed": True
            }

        # 2. Isolated temporary directory and script file
        temp_dir = tempfile.mkdtemp(prefix="agentx_sandbox_")
        temp_file_path = os.path.join(temp_dir, "script.py")

        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(code)

        # 3. Clean environment: strip all API keys and database credentials
        safe_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "TEMP": temp_dir,
            "TMP": temp_dir,
            "PYTHONIOENCODING": "utf-8"
        }

        try:
            # Run the script in isolated subprocess
            result = subprocess.run(
                [sys.executable, "-I", temp_file_path],  # -I flag isolates from user site-packages/env
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=temp_dir,
                env=safe_env
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
            try:
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"CodeExecutorTool: Failed to cleanup sandbox temp directory {temp_dir}: {e}")
