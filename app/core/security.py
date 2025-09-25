from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from typing import Dict, Optional

from .config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Pre-process users for faster token lookup
TOKEN_TO_USER_MAP = {
    details["token"]: {"username": username, **details}
    for username, details in settings.users.users.items()
}

async def get_user_info(token: str = Security(api_key_header)) -> Dict:
    """Dependency to verify API key and return user info."""
    user_info = TOKEN_TO_USER_MAP.get(token)
    if user_info:
        return user_info
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
