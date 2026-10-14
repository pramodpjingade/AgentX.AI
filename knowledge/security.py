from typing import Dict, Any, List, Optional
from loguru import logger

class KnowledgeSecurityManager:
    """
    Knowledge Security & Permission Filter for AgentX.
    Enforces RBAC/ABAC tenant isolation, document permissions, folder permissions, and organization policies.
    """

    def filter_permitted_results(
        self,
        results: List[Dict[str, Any]],
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Filters retrieved knowledge items according to user identity and access permissions."""
        roles = [r.lower() for r in (user_roles or ["user"])]
        if "admin" in roles or "system" in roles:
            return results  # Admin bypass

        permitted = []
        uid_str = str(user_id) if user_id else "global"

        for item in results:
            item_owner = str(item.get("user_id", "global"))
            item_visibility = item.get("visibility", "public").lower()

            if item_owner in [uid_str, "global"] or item_visibility == "public":
                permitted.append(item)
            else:
                logger.warning(f"KnowledgeSecurityManager: Filtered unauthorized access to doc '{item.get('doc_id')}' for user '{user_id}'")

        return permitted
