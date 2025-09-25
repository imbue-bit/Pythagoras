import re
from typing import Dict, List, Tuple, Set
from ..core.logger import log

class RBACManager:
    def __init__(self, rbac_config: Dict):
        self.roles_config = rbac_config.get('roles', {})
        log.info("RBACManager initialized.")

    def get_user_permissions(self, user_roles: List[str]) -> Dict:
        permissions = {"allowed_tables": set(), "allowed_operations": set()}
        for role in user_roles:
            if role in self.roles_config:
                role_perms = self.roles_config[role]
                # Handle wildcard for tables
                if "*" in role_perms.get('allowed_tables', []):
                    permissions['allowed_tables'] = {"*"}
                elif permissions['allowed_tables'] != {"*"}:
                    permissions['allowed_tables'].update(role_perms.get('allowed_tables', []))
                
                permissions['allowed_operations'].update(op.upper() for op in role_perms.get('allowed_operations', []))
        
        return {k: list(v) for k, v in permissions.items()}

    def validate_sql(self, sql_query: str, permissions: Dict) -> Tuple[bool, str]:
        sql_upper = sql_query.strip().upper()
        
        # 1. Validate operation
        detected_op = sql_upper.split()[0]
        if detected_op not in permissions.get('allowed_operations', []):
            msg = f"Operation '{detected_op}' is not allowed for this user's roles."
            log.warning(f"RBAC validation failed: {msg}")
            return False, msg

        # 2. Validate table access
        # This regex is a simplification. For production, consider a real SQL parser library.
        tables_in_query = set(re.findall(r'\b(?:FROM|JOIN|UPDATE|INTO)\s+([`"]?[a-zA-Z0-9_]+[`"]?)', sql_upper))
        # Clean up quotes
        cleaned_tables = {t.strip('`"') for t in tables_in_query}

        if "*" not in permissions.get('allowed_tables', []):
            allowed_tables = set(permissions['allowed_tables'])
            for table in cleaned_tables:
                if table.lower() not in allowed_tables:
                    msg = f"Access to table '{table}' is denied for this user's roles."
                    log.warning(f"RBAC validation failed: {msg}")
                    return False, msg
        
        log.info("RBAC validation successful for generated SQL.")
        return True, "SQL is compliant with user permissions."
