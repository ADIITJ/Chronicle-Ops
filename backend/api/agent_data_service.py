from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

def get_db():
    from ..shared.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/decisions/{run_id}")
async def get_agent_decisions(
    run_id: str,
    agent_role: str = None,
    db: Session = Depends(get_db)
):
    """Get agent decisions for a run"""
    from ..shared.agent_models import AgentDecision
    
    query = db.query(AgentDecision).filter(AgentDecision.run_id == run_id)
    
    if agent_role:
        query = query.filter(AgentDecision.agent_role == agent_role)
    
    decisions = query.order_by(AgentDecision.tick.desc()).limit(100).all()
    
    return [
        {
            "id": d.id,
            "tick": d.tick,
            "agent_role": d.agent_role,
            "observations": d.observations,
            "reasoning": d.reasoning,
            "proposed_actions": d.proposed_actions,
            "approved": d.approved,
            "executed": d.executed,
            "created_at": d.created_at.isoformat()
        }
        for d in decisions
    ]

@router.get("/market-state/{run_id}")
async def get_market_state(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get latest market state"""
    from ..shared.agent_models import MarketState
    
    state = db.query(MarketState).filter(
        MarketState.run_id == run_id
    ).order_by(MarketState.tick.desc()).first()
    
    if not state:
        return None
    
    return {
        "tick": state.tick,
        "sentiment_score": state.sentiment_score,
        "awareness_level": state.awareness_level,
        "trust_level": state.trust_level,
        "viral_coefficient": state.viral_coefficient,
        "market_dynamics": state.market_dynamics
    }

@router.get("/market-history/{run_id}")
async def get_market_history(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get market state history"""
    from ..shared.agent_models import MarketState
    
    states = db.query(MarketState).filter(
        MarketState.run_id == run_id
    ).order_by(MarketState.tick.asc()).all()
    
    return [
        {
            "tick": s.tick,
            "sentiment_score": s.sentiment_score,
            "awareness_level": s.awareness_level,
            "trust_level": s.trust_level,
            "viral_coefficient": s.viral_coefficient
        }
        for s in states
    ]

@router.get("/event-responses/{run_id}")
async def get_event_responses(
    run_id: str,
    db: Session = Depends(get_db)
):
    """Get event responses"""
    from ..shared.agent_models import EventResponse
    
    responses = db.query(EventResponse).filter(
        EventResponse.run_id == run_id
    ).order_by(EventResponse.tick.desc()).limit(50).all()
    
    return [
        {
            "id": r.id,
            "tick": r.tick,
            "event_id": r.event_id,
            "agent_role": r.agent_role,
            "response_text": r.response_text,
            "actions_taken": r.actions_taken
        }
        for r in responses
    ]
