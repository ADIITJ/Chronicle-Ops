from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from ..shared.auth import get_current_user, AuthContext
from ..shared.database import get_db_dependency
from ..shared.models import SimulationRun, RunStatus, CompanyBlueprint, EventTimeline, AgentConfig
from ..simulation.engine import SimulationEngine
from ..agents.orchestrator import AgentOrchestrator
from ..agents.ceo import CEOAgent
from ..agents.cfo import CFOAgent
from ..agents.coo import COOAgent
from ..policy.engine import PolicyEngine
from ..audit.ledger import AuditLedger
import json

router = APIRouter()

# In-memory storage for active simulations (in production, use Redis or similar)
active_simulations: Dict[str, SimulationEngine] = {}
active_orchestrators: Dict[str, AgentOrchestrator] = {}
audit_ledgers: Dict[str, AuditLedger] = {}

class CreateRunRequest(BaseModel):
    blueprint_id: str
    timeline_id: str
    agent_config_id: str
    seed: int

class TickRequest(BaseModel):
    ticks: int = 1

@router.post("/runs", status_code=status.HTTP_201_CREATED)
async def create_run(
    request: CreateRunRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Create new simulation run"""
    
    # Fetch configs
    blueprint = db.query(CompanyBlueprint).filter(
        CompanyBlueprint.id == request.blueprint_id
    ).first()
    
    timeline = db.query(EventTimeline).filter(
        EventTimeline.id == request.timeline_id
    ).first()
    
    agent_config = db.query(AgentConfig).filter(
        AgentConfig.id == request.agent_config_id
    ).first()
    
    if not blueprint or not timeline or not agent_config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    # Check tenant access
    if not auth.can_read(blueprint.tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check for duplicate run (idempotency)
    existing = db.query(SimulationRun).filter(
        SimulationRun.tenant_id == auth.tenant_id,
        SimulationRun.blueprint_id == request.blueprint_id,
        SimulationRun.timeline_id == request.timeline_id,
        SimulationRun.agent_config_id == request.agent_config_id,
        SimulationRun.seed == request.seed
    ).first()
    
    if existing:
        return {"id": existing.id, "message": "Run already exists"}
    
    # Create run record
    run = SimulationRun(
        tenant_id=auth.tenant_id,
        blueprint_id=request.blueprint_id,
        timeline_id=request.timeline_id,
        agent_config_id=request.agent_config_id,
        seed=request.seed,
        status=RunStatus.CREATED.value,
        created_by=auth.user_id
    )
    
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # Initialize simulation engine
    blueprint_dict = {
        'industry': blueprint.industry,
        'initial_conditions': blueprint.initial_conditions,
        'constraints': blueprint.constraints,
        'policies': blueprint.policies,
        'market_exposure': blueprint.market_exposure
    }
    
    timeline_dict = {
        'start_date': timeline.start_date.isoformat(),
        'end_date': timeline.end_date.isoformat(),
        'events': timeline.events
    }
    
    engine = SimulationEngine(
        blueprint=blueprint_dict,
        timeline=timeline_dict,
        seed=request.seed
    )
    
    # Initialize agents
    agents = []
    for agent_def in agent_config.agents:
        role = agent_def['role']
        if role == 'ceo':
            agents.append(CEOAgent(agent_def))
        elif role == 'cfo':
            agents.append(CFOAgent(agent_def))
        elif role == 'coo':
            agents.append(COOAgent(agent_def))
    
    # Initialize orchestrator
    policy_engine = PolicyEngine(blueprint.policies)
    orchestrator = AgentOrchestrator(agents, policy_engine, engine)
    
    # Initialize audit ledger
    ledger = AuditLedger()
    
    # Store in memory
    active_simulations[run.id] = engine
    active_orchestrators[run.id] = orchestrator
    audit_ledgers[run.id] = ledger
    
    return {"id": run.id, "status": run.status}

@router.post("/runs/{run_id}/start")
async def start_run(
    run_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Start simulation run"""
    
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if not auth.can_write(run.tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Idempotent: if already running, return success
    if run.status == RunStatus.RUNNING.value:
        return {"status": "already_running"}
    
    run.status = RunStatus.RUNNING.value
    run.started_at = datetime.utcnow()
    db.commit()
    
    return {"status": "started"}

@router.post("/runs/{run_id}/tick")
async def tick_simulation(
    run_id: str,
    request: TickRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Advance simulation by N ticks"""
    
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if not auth.can_write(run.tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    engine = active_simulations.get(run_id)
    orchestrator = active_orchestrators.get(run_id)
    ledger = audit_ledgers.get(run_id)
    
    if not engine or not orchestrator or not ledger:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    # Execute ticks
    for _ in range(request.ticks):
        # Agent decision cycle
        decisions = await orchestrator.run_decision_cycle()
        
        # Log to audit ledger
        for decision in decisions:
            ledger.append(
                run_id=run_id,
                sim_time=engine.current_time,
                entry_type="agent_decision",
                data=decision,
                agent_role=decision.get('action', {}).get('agent_role')
            )
        
        # Tick simulation
        can_continue = engine.tick()
        
        if not can_continue:
            run.status = RunStatus.COMPLETED.value
            run.completed_at = datetime.utcnow()
            break
    
    # Update run
    run.current_time = engine.current_time
    run.metrics = engine.get_metrics()
    db.commit()
    
    return {
        "current_time": engine.current_time.isoformat(),
        "metrics": engine.get_metrics(),
        "status": run.status
    }

@router.get("/runs/{run_id}/state")
async def get_run_state(
    run_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Get current simulation state"""
    
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if not auth.can_read(run.tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    engine = active_simulations.get(run_id)
    if not engine:
        # Return persisted state
        return {
            "status": run.status,
            "current_time": run.current_time.isoformat() if run.current_time else None,
            "metrics": run.metrics
        }
    
    return {
        "status": run.status,
        "current_time": engine.current_time.isoformat(),
        "state": engine.state.to_dict(),
        "metrics": engine.get_metrics()
    }

@router.get("/runs/{run_id}/audit")
async def get_audit_trail(
    run_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Get audit trail for run"""
    
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if not auth.can_read(run.tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    ledger = audit_ledgers.get(run_id)
    if not ledger:
        return {"entries": []}
    
    return {
        "entries": ledger.get_entries(run_id),
        "verified": ledger.verify_chain()
    }
