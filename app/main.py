from fastapi import FastAPI, Depends, HTTPException
from typing import Dict

from .core.config import settings
from .core.pythagoras_core import Pythagoras
from .core.security import get_user_info
from .models.pydantic_models import QueryRequest, QueryResponse, ErrorResponse
from .core.logger import log

app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="An AI-powered middleware for interacting with databases using natural language."
)

# Initialize the core service once on startup
try:
    pythagoras_service = Pythagoras()
except Exception as e:
    log.critical(f"FATAL: Failed to initialize Pythagoras Core Service: {e}")
    # In a real app, you might want to exit or handle this more gracefully
    pythagoras_service = None

@app.on_event("startup")
async def startup_event():
    if pythagoras_service is None:
        log.error("Application is starting in a non-functional state due to initialization failure.")
    else:
        log.info("Application startup complete. Pythagoras is ready.")

@app.post(
    "/v1/query",
    response_model=QueryResponse,
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}}
)
async def handle_query(request: QueryRequest, user_info: Dict = Depends(get_user_info)):
    """
    Accepts a natural language query, converts it to SQL, executes it, and returns the result.
    Requires a valid API Key in the `X-API-Key` header.
    """
    if not pythagoras_service:
        raise HTTPException(status_code=503, detail="Service Unavailable: Core service failed to initialize.")
    
    result = pythagoras_service.process_query(request.query, user_info)
    
    if "error" in result:
        # Differentiate between bad requests and permission issues
        if "denied" in result["error"].lower() or "unauthorized" in result["error"].lower():
             raise HTTPException(status_code=403, detail=result["error"])
        else:
             raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Provides a simple health check endpoint."""
    if pythagoras_service and pythagoras_service.db.engine:
        return {"status": "ok"}
    return {"status": "degraded"}
