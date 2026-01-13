from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from typing import Dict, Any
import time
from ..shared.auth import get_current_user, AuthContext
from ..shared.database import get_db_dependency
from sqlalchemy.orm import Session
import redis
import os

app = FastAPI(
    title="ChronicleOps API",
    description="Time-locked multi-agent company simulation platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for rate limiting
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Rate limiting middleware
async def rate_limit_check(auth: AuthContext = Depends(get_current_user)):
    """Rate limit: 100 requests per minute per tenant"""
    key = f"rate_limit:{auth.tenant_id}"
    count = redis_client.incr(key)
    
    if count == 1:
        redis_client.expire(key, 60)
    
    if count > 100:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return auth

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ChronicleOps API Gateway",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Import routers
from .config_service import router as config_router
from .simulation_service import router as simulation_router

app.include_router(config_router, prefix="/api/v1/config", tags=["config"])
app.include_router(simulation_router, prefix="/api/v1/simulation", tags=["simulation"])
