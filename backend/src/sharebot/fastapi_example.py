"""
FastAPI Integration Example for ShareBot

This file shows how to integrate ShareBot into your FastAPI application.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sharebot.main_sharebot import ShareBot

# -------------------------------------------------------
# FastAPI App
# -------------------------------------------------------
app = FastAPI(
    title="ShareBot API",
    description="Financial chatbot API for Indian stock markets",
    version="1.0.0"
)

# -------------------------------------------------------
# Request/Response Models
# -------------------------------------------------------
class ChatRequest(BaseModel):
    """Chat request model"""
    query: str
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the current price of TCS?",
                "session_id": "user123"
            }
        }


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "**TCS Current Price**: ₹3,245.50 🔺 +1.2%",
                "session_id": "user123"
            }
        }


# -------------------------------------------------------
# Global ShareBot Instance (or use session-based)
# -------------------------------------------------------
sharebot = ShareBot()


# -------------------------------------------------------
# API Endpoints
# -------------------------------------------------------

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ShareBot API",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for ShareBot.
    
    Args:
        request: ChatRequest with query and optional session_id
    
    Returns:
        ChatResponse with markdown formatted response
    """
    try:
        # Process query
        response = sharebot.chat(request.query, request.session_id)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint for ShareBot.
    
    Args:
        request: ChatRequest with query and optional session_id
    
    Returns:
        StreamingResponse with markdown formatted chunks
    """
    from fastapi.responses import StreamingResponse
    
    try:
        # Create streaming generator
        def generate():
            for chunk in sharebot.chat_stream(request.query, request.session_id):
                yield chunk
        
        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/clear-memory")
async def clear_memory(session_id: Optional[str] = None):
    """
    Clear conversation memory.
    
    Args:
        session_id: Optional session ID (for future session-based memory)
    
    Returns:
        Success message
    """
    try:
        sharebot.clear_memory()
        return {"status": "success", "message": "Memory cleared"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """
    Get ShareBot performance metrics.
    
    Returns:
        Performance metrics
    """
    try:
        metrics = sharebot.get_metrics()
        return metrics
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# Run Server
# -------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    
    print("Starting ShareBot API server...")
    print("API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
