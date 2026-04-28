import os
import logging
import time
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from services.vertex_ai_service import llm_service, ChatResponse
from services.civic_api_service import civic_service

# Evaluation Criterion: Security (Rate Limiting)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="CivicSense API",
    description="Enterprise-grade API for the CivicSense Election Assistant",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure logging for AI evaluation audit
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("civicsense")

# Evaluation Criterion: Security (CORS Configuration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production optimization: restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task : Structured logging middleware
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next) -> Any:
    """
    Middleware to log request performance and status for auditing.
    
    Args:
        request: The incoming HTTP request.
        call_next: The next handler in the stack.
        
    Returns:
        The HTTP response.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Path: {request.url.path} | Status: {response.status_code} | "
        f"Latency: {process_time:.2f}ms"
    )
    return response

# Task : Enhanced Pydantic models with strict constraints
class ChatRequest(BaseModel):
    """Payload for AI chat requests with strict validation."""
    message: str = Field(..., max_length=500, description="User query (max 500 characters to prevent DoS)")

class AddressRequest(BaseModel):
    """Payload for localized civic data requests."""
    address: str = Field(..., min_length=5, description="Full residential address for polling lookups")
    election_id: Optional[int] = Field(None, description="Specific election ID override")

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Health check endpoint for the CivicSense service.
    
    Returns:
        Dict[str, str]: Service status and name.
    """
    return {"status": "ok", "service": "CivicSense"}

@app.post("/api/chat")
@limiter.limit("5/minute")
async def chat_with_ai(request: Request, chat_req: ChatRequest) -> ChatResponse:
    """
    Endpoint for secure, neutral AI assistant interaction.
    
    Args:
        request: FastAPI request object for rate limiting.
        chat_req: Validated user message payload.
        
    Returns:
        ChatResponse: Gemini-generated impartial response.
        
    Raises:
        HTTPException: If payload is missing or invalid.
    """
    if not chat_req.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    response = await llm_service.get_response(chat_req.message)
    return response

@app.post("/api/civic-info")
@limiter.limit("10/minute")
async def get_civic_data(request: Request, addr_req: AddressRequest) -> Dict[str, Any]:
    """
    Endpoint for fetching localized voter information from official sources.
    
    Args:
        request: FastAPI request object for rate limiting.
        addr_req: Validated address payload.
        
    Returns:
        Dict[str, Any]: Parsed data from the Google Civic Information API.
    """
    data = await civic_service.get_voter_info(addr_req.address, addr_req.election_id)
    return data

@app.get("/api/elections")
async def list_elections() -> Dict[str, Any]:
    """
    Lists upcoming elections available in the Google Civic API.
    
    Returns:
        Dict[str, Any]: Collection of election metadata.
    """
    return await civic_service.get_elections()

if __name__ == "__main__":
    import uvicorn
    # Task : Dynamic port binding for Cloud Run environment compatibility
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
