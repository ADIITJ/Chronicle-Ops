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
            current_tick=0,
            started_by=None
        )
        
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
        "current_tick": run.current_tick,
        "seed": run.seed,
        "created_at": run.created_at.isoformat()
    }
