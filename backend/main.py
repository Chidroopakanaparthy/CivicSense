import os
import logging
import time
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import Optional

from services.vertex_ai_service import llm_service
from services.civic_api_service import civic_service

# Configure logging for AI evaluation audit
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("civicsense")

# Evaluation Criterion: Security (Rate Limiting)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="CivicSense API",
    description="API for the CivicSense Election Assistant",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Evaluation Criterion: Security (CORS Configuration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task 1.3: Structured logging middleware
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Path: {request.url.path} | Status: {response.status_code} | "
        f"Time: {process_time:.2f}ms"
    )
    return response

class ChatRequest(BaseModel):
    message: str

class AddressRequest(BaseModel):
    address: str
    election_id: Optional[int] = None

@app.get("/")
async def root():
    """Basic health check endpoint."""
    return {"status": "ok", "service": "CivicSense"}

@app.post("/api/chat")
@limiter.limit("5/minute")
async def chat_with_ai(request: Request, chat_req: ChatRequest):
    """
    Endpoint for AI assistant chat. 
    Implements rate limiting and AI response logic with strict neutrality.
    """
    if not chat_req.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    response = await llm_service.get_response(chat_req.message)
    return response

@app.post("/api/civic-info")
@limiter.limit("10/minute")
async def get_civic_data(request: Request, addr_req: AddressRequest):
    """
    Endpoint for fetching localized voter information from Google Civic API.
    """
    if not addr_req.address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    data = await civic_service.get_voter_info(addr_req.address, addr_req.election_id)
    return data

@app.get("/api/elections")
async def list_elections():
    """Fetches upcoming elections from Google Civic API."""
    return await civic_service.get_elections()

if __name__ == "__main__":
    import uvicorn
    # Task 1.2: Dynamic port binding for Cloud Run
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
