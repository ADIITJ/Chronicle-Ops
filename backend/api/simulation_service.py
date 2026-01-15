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
        initial_metrics = {
            "cash": 0,
            "revenue": 0, # Legacy key
            "revenue_monthly": 0,
            "costs_monthly": 0,
            "headcount": 0,
            "growth": 0.0, # Legacy key
            "growth_rate": 0.0,
            "runway_months": 0,
            "service_level": 1.0,
            "compliance_score": 1.0
        }
        
        # We need to fetch blueprint to set initial metrics properly
        from shared.models import CompanyBlueprint
        blueprint = db.query(CompanyBlueprint).filter(CompanyBlueprint.id == request.blueprint_id).first()
        if blueprint and blueprint.initial_conditions:
             ic = blueprint.initial_conditions
             cash = ic.get("cash", 0)
             monthly_burn = ic.get("monthly_burn", 0)
             
             initial_metrics.update({
                 "cash": cash,
                 "revenue": 0,
                 "revenue_monthly": 0,
                 "costs_monthly": monthly_burn,
                 "headcount": ic.get("headcount", 0),
                 "growth": 0.0,
                 "growth_rate": 0.0,
                 "runway_months": cash / monthly_burn if monthly_burn > 0 else 0,
                 "service_level": 1.0,
                 "compliance_score": 1.0
             })
        
        run.metrics = initial_metrics
        
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
    
    # Simulate changes
    import random
    from shared.models import EventTimeline, AgentConfig
    from shared.agent_models import AgentDecision, EventResponse
    from .agent_logic import run_agent_turn
    
    metrics = run.metrics or {}
    cash = metrics.get("cash", 1000000)
    burn = metrics.get("monthly_burn", 50000)
    revenue = metrics.get("revenue", 0)
    current_tick = run.current_tick or 0 # We need to track ticks somewhere. Using 'or 0' if missing.
    
    # Get configuration context
    timeline = db.query(EventTimeline).filter(EventTimeline.id == run.timeline_id).first()
    agent_config = db.query(AgentConfig).filter(AgentConfig.id == run.agent_config_id).first()
    
    # Apply changes over ticks
    for _ in range(request.ticks):
        current_tick += 1
        run.current_time += timedelta(days=1)
        
        # 1. Check for Events
        active_events = []
        if timeline and timeline.events:
            for evt in timeline.events:
                # Simple check for exact tick match
                if evt.get("tick") == current_tick:
                    active_events.append(evt)
        
        # 2. Trigger Agents if Event or Random (1% chance)
        if active_events or random.random() < 0.05:
            # Gather state for LLM
            company_state = {"metrics": {**metrics, "cash": cash, "revenue": revenue, "monthly_burn": burn}}
            
            if agent_config and agent_config.agents:
                for agent_profile in agent_config.agents:
                    # Run LLM Turn
                    decision_data = await run_agent_turn(
                        agent_role=agent_profile.get("role", "Unknown"),
                        company_state=company_state,
                        world_events=active_events,
                        agent_profile=agent_profile
                    )
                    
                    # Store Decision
                    decision = AgentDecision(
                        run_id=run.id,
                        tick=current_tick,
                        agent_role=agent_profile.get("role"),
                        observations={"events": active_events, "metrics": company_state},
                        reasoning=decision_data.get("reasoning", ""),
                        proposed_actions=decision_data.get("actions", {}),
                        approved=True,
                        executed=True
                    )
                    db.add(decision)
                    
                    # Store Event Response specifically if there was an event
                    for evt in active_events:
                        resp = EventResponse(
                            run_id=run.id,
                            event_id=str(evt.get("tick")), # minimal ID
                            tick=current_tick,
                            agent_role=agent_profile.get("role"),
                            event_type=evt.get("type", "unknown"),
                            event_description=evt.get("description", ""),
                            agent_response=decision_data.get("thought_process") or decision_data.get("reasoning"),
                            actions_taken=decision_data.get("actions", {})
                        )
                        db.add(resp)
                    
                    # Apply Actions to Metrics (Simplified)
                    actions = decision_data.get("actions", {})
                    if "cost_cut" in actions:
                        burn *= 0.95
                    if "marketing_spend" in actions:
                        cash -= 10000
                        revenue *= 1.02
        
        # Standard financial loop
        daily_burn = burn / 30
        daily_revenue = revenue / 30
        
        if random.random() < 0.1:
            daily_revenue *= 1.05 # Organic Growth
        
        cash = cash - daily_burn + daily_revenue
        
    # Update metrics
    run.current_tick = current_tick # Need to ensure model has this or handle it
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
