from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter()

def get_db():
    from shared.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StartSimulationRequest(BaseModel):
    blueprint_id: str
    timeline_id: str
    agent_config_id: str
    seed: Optional[int] = None

@router.post("/runs")
async def start_simulation(
    request: StartSimulationRequest,
    db: Session = Depends(get_db)
):
    """Start a new simulation run"""
    from shared.models import SimulationRun
    
    try:
        run = SimulationRun(
            id=str(uuid.uuid4()),
            tenant_id="default-tenant",
            blueprint_id=request.blueprint_id,
            timeline_id=request.timeline_id,
            agent_config_id=request.agent_config_id,
            seed=request.seed or int(datetime.utcnow().timestamp()),
            status="running",
            # current_tick is not in model, potentially handle in metrics
            # started_by is not in model
        )
        
        # Initialize metrics if needed
        run.metrics = {
            "cash": 0, # Should be from blueprint
            "revenue": 0,
            "headcount": 0,
            "growth": 0.0
        }
        
        # We need to fetch blueprint to set initial metrics properly
        from shared.models import CompanyBlueprint
        blueprint = db.query(CompanyBlueprint).filter(CompanyBlueprint.id == request.blueprint_id).first()
        if blueprint and blueprint.initial_conditions:
             ic = blueprint.initial_conditions
             run.metrics = {
                 "cash": ic.get("cash", 0),
                 "revenue": 0,
                 "headcount": ic.get("headcount", 0),
                 "growth": 0.0
             }
        
        db.add(run)
        db.commit()
        db.refresh(run)
        
        return {
            "id": run.id,
            "status": run.status,
            "seed": run.seed
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs/{run_id}")
async def get_simulation_run(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get simulation run details"""
    from shared.models import SimulationRun
    
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "id": run.id,
        "status": run.status,
        "seed": run.seed,
        "created_at": run.created_at.isoformat()
    }

class TickRequest(BaseModel):
    ticks: int = 1

@router.post("/runs/{run_id}/tick")
async def tick_simulation(
    run_id: str,
    request: TickRequest,
    db: Session = Depends(get_db)
):
    """Advance simulation by N ticks"""
    from shared.models import SimulationRun
    from datetime import timedelta
    
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    # Initialize logic
    if not run.current_time:
         run.current_time = datetime.utcnow() # Should use timeline start date properly
    
    # Simulate changes (basic mock logic for MVP)
    import random
    metrics = run.metrics or {}
    cash = metrics.get("cash", 1000000)
    burn = metrics.get("monthly_burn", 50000)
    revenue = metrics.get("revenue", 0)
    
    # Apply changes over ticks
    for _ in range(request.ticks):
        # 1 day per tick? Let's say 1 tick = 1 day
        run.current_time += timedelta(days=1)
        
        # Simple math
        daily_burn = burn / 30
        daily_revenue = revenue / 30
        
        # Random fluctuation
        if random.random() < 0.1:
            daily_revenue *= 1.05 # Growth
        
        cash = cash - daily_burn + daily_revenue
        
    # Update metrics
    run.metrics = {
        **metrics,
        "cash": cash,
        "revenue": revenue * 1.01, # slight organic growth
        "monthly_burn": burn,
        "runway_months": cash / burn if burn > 0 else 999
    }
    
    db.commit()
    
    return {
        "status": run.status,
        "current_time": run.current_time,
        "metrics": run.metrics
    }

@router.get("/runs/{run_id}/state")
async def get_simulation_state(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get current state including metrics"""
    from shared.models import SimulationRun
    
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    return {
        "status": run.status,
        "current_time": run.current_time or datetime.utcnow(),
        "metrics": run.metrics or {}
    }
