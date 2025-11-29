import os
import json
import logging
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from Schemas import QueryRequest, QueryResponse

# Import the three main modules
from src.sharebot.main_sharebot import ShareBot
from src.kite.portbot.chatbot import KiteChatbot
from src.kite.portrep.portreport.run_portfolio_report import main as generate_portfolio_report

# ─────────────────────────────────────────────
# 🪵 Logging
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MainAPI")

# ─────────────────────────────────────────────
# 🌐 Lifespan Initialization
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing services...")
        
        # Initialize Market Chatbot
        app.state.market_chatbot = ShareBot()
        logger.info("✅ Market Chatbot ready")
        
        # Initialize Portfolio Chatbot (shared instance)
        app.state.portfolio_chatbot = await KiteChatbot().__aenter__()
        logger.info("✅ Portfolio Chatbot ready")
        
        yield
        
        # Cleanup
        if hasattr(app.state, 'portfolio_chatbot'):
            await app.state.portfolio_chatbot.__aexit__(None, None, None)
            logger.info("✅ Portfolio Chatbot cleaned up")
            
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise

app = FastAPI(
    title="KiteInfi API",
    version="1.0.0",
    description="Unified API for Market Chat, Portfolio Chat, and Portfolio Reports",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# 📊 1️⃣ MARKET CHATBOT (ShareBot)
# ─────────────────────────────────────────────

@app.post("/market_chatbot/stream")
async def market_chatbot_stream(request: QueryRequest):
    """Market chatbot with streaming response"""
    chatbot = app.state.market_chatbot
    user_query = request.user_query.strip()
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    async def generate_stream():
        try:
            for chunk in chatbot.chat_stream(user_query):
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
                await asyncio.sleep(0)
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Market chatbot stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/market_chatbot/sync", response_model=QueryResponse)
async def market_chatbot_sync(request: QueryRequest):
    """Market chatbot with synchronous response"""
    chatbot = app.state.market_chatbot
    user_query = request.user_query.strip()
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        response = chatbot.chat(user_query)
        return QueryResponse(response=response)
    
    except Exception as e:
        logger.error(f"Market chatbot sync error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# 💼 2️⃣ PORTFOLIO CHATBOT (KiteChatbot)
# ─────────────────────────────────────────────

@app.post("/portfolio_chatbot/stream")
async def portfolio_chatbot_stream(request: QueryRequest):
    """Portfolio chatbot with streaming response"""
    bot = app.state.portfolio_chatbot
    user_query = request.user_query.strip()
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    async def generate_stream():
        try:
            # Get full response first
            response = await bot.chat(user_query)
            
            # Stream the response character by character
            for char in response:
                yield f"data: {json.dumps({'content': char, 'done': False})}\n\n"
                await asyncio.sleep(0.01)  # Smooth streaming
            
            yield f"data: {json.dumps({'done': True})}\n\n"
                    
        except Exception as e:
            logger.error(f"Portfolio chatbot stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/portfolio_chatbot/sync", response_model=QueryResponse)
async def portfolio_chatbot_sync(request: QueryRequest):
    """Portfolio chatbot with synchronous response"""
    bot = app.state.portfolio_chatbot
    user_query = request.user_query.strip()
    
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        response = await bot.chat(user_query)
        return QueryResponse(response=response)
                
    except Exception as e:
        logger.error(f"Portfolio chatbot sync error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# 📈 3️⃣ PORTFOLIO REPORT GENERATOR
# ─────────────────────────────────────────────

@app.post("/portfolio_report")
async def portfolio_report():
    """Generate and email portfolio report"""
    try:
        logger.info("Starting portfolio report generation...")
        
        # Run the portfolio report generation
        await generate_portfolio_report()
        
        return {
            "status": "success",
            "message": "Portfolio report generated and emailed successfully"
        }
        
    except Exception as e:
        logger.error(f"Portfolio report error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# 🩺 Health Check
# ─────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "market_chatbot": "ready",
            "portfolio_chatbot": "ready",
            "portfolio_report": "ready"
        }
    }


# ─────────────────────────────────────────────
# 🚀 Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting KiteInfi API on port {port}...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
