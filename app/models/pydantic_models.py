from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="The natural language query to be executed.")

class QueryResult(BaseModel):
    status: str
    data: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None

class QueryResponse(BaseModel):
    source: str = Field(description="Indicates if the result is from 'cache' or 'live' execution.")
    natural_language_query: str
    generated_sql: str
    result: QueryResult

class ErrorResponse(BaseModel):
    error: str
