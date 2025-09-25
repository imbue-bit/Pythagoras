from ..core.config import settings
from ..core.logger import log
from ..services.db_manager import DBManager
from ..services.llm_handler import LLMHandler
from ..services.cache_manager import CacheManager
from ..services.rbac_manager import RBACManager

class Pythagoras:
    def __init__(self):
        self.db = DBManager(settings.database)
        self.llm = LLMHandler(settings.llm)
        self.cache = CacheManager(settings.cache.max_size, settings.cache.ttl)
        self.rbac = RBACManager(settings.rbac.model_dump())
        self.schema_info = self.db.schema_info
        log.info("Pythagoras Core Service initialized successfully.")

    def process_query(self, nl_query: str, user_info: dict):
        username = user_info.get("username", "unknown")
        user_roles = user_info.get("roles", [])
        log.info(f"Processing query for user '{username}' with roles {user_roles}: '{nl_query}'")

        # 1. Generate cache key and check cache
        cache_key = self.cache.generate_key(nl_query, user_roles)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return {"source": "cache", **cached_result}

        # 2. Get user permissions based on roles
        permissions = self.rbac.get_user_permissions(user_roles)
        if not permissions.get("allowed_tables"):
            log.warning(f"Access denied for user '{username}'. No permissions found for roles {user_roles}.")
            return {"error": "Access denied. Your roles do not grant access to any data."}

        # 3. Generate SQL using LLM with RBAC constraints
        generated_sql = self.llm.generate_sql(nl_query, self.schema_info, permissions)
        if not generated_sql or "ACCESS DENIED" in generated_sql.upper() or "ERROR" in generated_sql.upper():
             log.warning(f"LLM denied access or failed to generate SQL for query: '{nl_query}'")
             return {"error": "Access Denied or failed to generate SQL. The query may involve unauthorized data or be invalid."}

        # 4. Final RBAC and security validation on the generated SQL
        is_valid, message = self.rbac.validate_sql(generated_sql, permissions)
        if not is_valid:
            log.error(f"SECURITY ALERT: SQL validation failed for user '{username}'. Reason: {message}. SQL: '{generated_sql}'")
            return {"error": f"Generated query failed security validation: {message}"}

        # 5. Execute SQL against the database
        result = self.db.execute_query(generated_sql)

        # 6. Cache the successful result and return
        response = {
            "natural_language_query": nl_query,
            "generated_sql": generated_sql,
            "result": result
        }
        if result.get("status") == "success":
            self.cache.set(cache_key, response)
        
        return {"source": "live", **response}
