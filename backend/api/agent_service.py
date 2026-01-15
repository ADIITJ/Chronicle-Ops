from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

def get_db():
    from ..shared.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AgentDecisionRequest(BaseModel):
    run_id: str
    tick: int
    context: Dict[str, Any]

@router.post("/decide")
async def agent_decide(
    request: AgentDecisionRequest,
    db: Session = Depends(get_db)
):
    """Trigger agent decision-making"""
    return {"status": "decisions_made", "tick": request.tick}

@router.get("/decisions/{run_id}")
async def get_agent_decisions(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get agent decisions for a run"""
    from shared.agent_models import AgentDecision
    
    decisions = db.query(AgentDecision).filter(
        AgentDecision.run_id == run_id
    ).order_by(AgentDecision.tick.desc()).limit(50).all()
    
    return [
        {
            "id": d.id,
            "tick": d.tick,
            "agent_role": d.agent_role,
            "reasoning": d.reasoning,
            "approved": d.approved
        }
        for d in decisions
    ]
