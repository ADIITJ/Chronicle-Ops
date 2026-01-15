from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import os

app = FastAPI(
    title="ChronicleOps API",
    description="Autonomous Company Simulation Platform",
    version="1.0.0"
)

# CORS middleware - allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database with required seed data"""
    try:
        from shared.database import SessionLocal
        from shared.models import Tenant
        
        db = SessionLocal()
        try:
            # Check for default tenant
            default_tenant = db.query(Tenant).filter(Tenant.id == "default-tenant").first()
            
            if not default_tenant:
                print("🌱 Seeding default tenant...")
                from datetime import datetime
                
                tenant = Tenant(
                    id="default-tenant",
                    name="ChronicleOps Demo Tenant",
                    created_at=datetime.utcnow()
                )
                db.add(tenant)
                db.commit()
                print("✅ Default tenant created")
            else:
                print("✅ Default tenant exists")
                
        except Exception as e:
            print(f"❌ Database seed failed: {str(e)}")
            # Don't crash startup, but log error
        finally:
            db.close()
    except ImportError:
        print("⚠️ Warning: Could not import shared modules for seeding")

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
from .agent_service import router as agent_router
from .policy_service import router as policy_router
from .agent_data_service import router as agent_data_router

# Include routers with correct prefixes
app.include_router(config_router, prefix="/api/v1/config", tags=["config"])
app.include_router(simulation_router, prefix="/api/v1/simulation", tags=["simulation"])
app.include_router(agent_router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(policy_router, prefix="/api/v1/policy", tags=["policy"])
app.include_router(agent_data_router, prefix="/api/v1/agent-data", tags=["agent-data"])
