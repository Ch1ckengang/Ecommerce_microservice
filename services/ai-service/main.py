"""
AI Service - FastAPI Application
Provides recommendation and chatbot endpoints
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from routers import recommend, chatbot, health, smart_recommend
from routers import phase9_recommend
from services.ai_manager import AIManager

# Global AI manager instance
ai_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    global ai_manager
    print("🚀 Starting AI Service...")
    
    ai_manager = AIManager()
    await ai_manager.initialize()
    
    # Store in app state
    app.state.ai_manager = ai_manager
    
    print("✅ AI Service started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Service...")
    await ai_manager.cleanup()
    print("✅ AI Service stopped")

# Create FastAPI app
app = FastAPI(
    title="AI Recommendation Service",
    description="Hệ thống gợi ý sản phẩm sử dụng LSTM, Knowledge Graph và RAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(recommend.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(smart_recommend.router, prefix="/api/v1", tags=["Smart Recommendations"])
app.include_router(chatbot.router, prefix="/api/v1", tags=["Chatbot"])
# Phase 9 - Multi-Model Ensemble (NEW - does not affect existing endpoints)
app.include_router(phase9_recommend.router, prefix="/api/v1", tags=["Phase 9 - Multi-Model"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Recommendation Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
