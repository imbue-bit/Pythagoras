from cachetools import TTLCache
from ..core.logger import log

class CacheManager:
    def __init__(self, max_size: int, ttl: int):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)
        log.info(f"CacheManager initialized with max_size={max_size}, ttl={ttl}s")

    def get(self, key: str):
        result = self.cache.get(key)
        if result:
            log.info(f"Cache HIT for key: {key}")
        else:
            log.info(f"Cache MISS for key: {key}")
        return result

    def set(self, key: str, value: any):
        log.info(f"Setting cache for key: {key}")
        self.cache[key] = value

    def generate_key(self, nl_query: str, user_roles: list[str]) -> str:
        roles_str = ",".join(sorted(user_roles))
        return f"user_roles={roles_str}::query={nl_query.lower().strip()}"
