from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..shared.database import get_db
from ..shared.agent_models import AgentDecision, MarketState, EventResponse
from ..shared.auth import get_current_user

router = APIRouter(prefix="/api/v1/simulation/runs", tags=["agent-data"])

@router.get("/{run_id}/agent-decisions")
async def get_agent_decisions(
    run_id: str,
    agent: str = "all",
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Get agent decision history"""
    query = db.query(AgentDecision).filter(AgentDecision.run_id == run_id)
    
    if agent != "all":
        query = query.filter(AgentDecision.agent_role == agent)
    
    decisions = query.order_by(AgentDecision.tick.desc()).limit(limit).all()
    
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

@router.get("/{run_id}/market-state")
async def get_current_market_state(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Get current market state"""
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
        "market_dynamics": state.market_dynamics,
        "price_perception": state.price_perception,
        "quality_perception": state.quality_perception,
        "brand_strength": state.brand_strength
    }

@router.get("/{run_id}/market-history")
async def get_market_history(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Get market state history"""
    states = db.query(MarketState).filter(
        MarketState.run_id == run_id
    ).order_by(MarketState.tick.asc()).all()
    
    current = states[-1] if states else None
    
    return {
        "current": {
            "sentiment_score": current.sentiment_score,
            "awareness_level": current.awareness_level,
            "trust_level": current.trust_level,
            "viral_coefficient": current.viral_coefficient,
            "market_dynamics": current.market_dynamics
        } if current else None,
        "history": [
            {
                "tick": s.tick,
                "sentiment_score": s.sentiment_score,
                "awareness_level": s.awareness_level,
                "trust_level": s.trust_level,
                "viral_coefficient": s.viral_coefficient,
                "demand_multiplier": s.market_dynamics.get("demand_multiplier", 1.0)
            }
            for s in states
        ]
    }

@router.get("/{run_id}/event-responses")
async def get_event_responses(
    run_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Get agent responses to events"""
    responses = db.query(EventResponse).filter(
        EventResponse.run_id == run_id
    ).order_by(EventResponse.tick.desc()).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "tick": r.tick,
            "agent_role": r.agent_role,
            "event_type": r.event_type,
            "event_description": r.event_description,
            "agent_response": r.agent_response,
            "actions_taken": r.actions_taken,
            "response_time_ms": r.response_time_ms,
            "created_at": r.created_at.isoformat()
        }
        for r in responses
    ]
