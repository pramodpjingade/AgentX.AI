from typing import List, Dict, Any, Optional
from loguru import logger
from tools.base_tool import BaseTool, ToolResult

class ToolSecurityManager:
    """
    Tool Security & Permission Enforcement Layer for AgentX.
    Validates user/role permissions before executing potentially dangerous tools.
    """

    DEFAULT_ALLOWED_PERMISSIONS = [
        "web_search",
        "weather",
        "maps",
        "read_file",
        "python_interpreter",
        "http_api",
        "document_generator",
        "vector_search"
    ]

    STRICT_PERMISSIONS = [
        "system_command",
        "write_file",
        "database_write",
        "email_send",
        "browser_automation"
    ]

    def __init__(self, user_role: str = "developer", granted_permissions: Optional[List[str]] = None):
        self.user_role = user_role
        self.granted_permissions = granted_permissions or self.DEFAULT_ALLOWED_PERMISSIONS.copy()
        if user_role in ["admin", "developer"]:
            self.granted_permissions.extend(self.STRICT_PERMISSIONS)

    def validate_tool_access(self, tool: BaseTool, user_permissions: Optional[List[str]] = None) -> bool:
        """
        Validates if the active user context possesses all required permissions for the target tool.
        """
        required = tool.permissions
        if not required:
            return True  # Tool requires no explicit permissions

        active_perms = set(self.granted_permissions)
        if user_permissions:
            active_perms.update(user_permissions)

        for perm in required:
            if perm not in active_perms:
                logger.warning(f"ToolSecurityManager: Permission denied for tool '{tool.name}'. Missing permission: '{perm}'")
                return False

        return True

    def create_permission_denied_result(self, tool_name: str, missing_permissions: List[str]) -> ToolResult:
        """Returns a standardized permission denied ToolResult."""
        return ToolResult(
            status="permission_denied",
            success=False,
            data=None,
            logs=[f"Permission denied for tool '{tool_name}'."],
            errors=[f"Access Denied: Missing permissions {missing_permissions}"]
        )
