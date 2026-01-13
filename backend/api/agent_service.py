from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ..shared.auth import get_current_user, AuthContext
from ..shared.database import get_db_dependency
from ..shared.observability import logger, metrics
from ..agents.orchestrator import AgentOrchestrator
from ..policy.engine import PolicyEngine
from ..simulation.engine import SimulationEngine

router = APIRouter()

# In-memory storage (production: use Redis)
active_orchestrators: Dict[str, AgentOrchestrator] = {}

class ApproveActionRequest(BaseModel):
    action_id: str
    approved_by: str

@router.get("/runs/{run_id}/pending-approvals")
async def get_pending_approvals(
    run_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Get all pending approvals for a run"""
    
    logger.info("Fetching pending approvals", run_id=run_id, user_id=auth.user_id)
    
    orchestrator = active_orchestrators.get(run_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Orchestrator not found")
    
    pending = orchestrator.get_pending_approvals()
    
    return {
        "run_id": run_id,
        "pending_approvals": pending,
        "count": len(pending)
    }

@router.post("/runs/{run_id}/approve-action")
async def approve_action(
    run_id: str,
    request: ApproveActionRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Approve a pending action"""
    
    logger.info("Approving action",
               run_id=run_id,
               action_id=request.action_id,
               approved_by=request.approved_by)
    
    orchestrator = active_orchestrators.get(run_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Orchestrator not found")
    
    success = orchestrator.approve_action(request.action_id, request.approved_by)
    
    if success:
        metrics.record_metric("action_approvals", 1, {"run_id": run_id})
        return {"status": "approved", "action_id": request.action_id}
    else:
        raise HTTPException(status_code=404, detail="Action not found or already processed")

@router.get("/runs/{run_id}/agent-summary")
async def get_agent_summary(
    run_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Get summary of all agents in a run"""
    
    orchestrator = active_orchestrators.get(run_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Orchestrator not found")
    
    return {
        "run_id": run_id,
        "agents": orchestrator.get_agent_summary()
    }

@router.post("/runs/{run_id}/trigger-decision-cycle")
async def trigger_decision_cycle(
    run_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Manually trigger an agent decision cycle"""
    
    logger.info("Triggering decision cycle", run_id=run_id)
    
    orchestrator = active_orchestrators.get(run_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Orchestrator not found")
    
    results = await orchestrator.run_decision_cycle()
    
    metrics.record_metric("decision_cycles", 1, {"run_id": run_id})
    
    return {
        "run_id": run_id,
        "decisions": results,
        "count": len(results)
    }
