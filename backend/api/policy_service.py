from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
from ..shared.auth import get_current_user, AuthContext
from ..shared.database import get_db_dependency
from ..shared.observability import logger, metrics
from ..policy.engine import PolicyEngine, PolicyDecision

router = APIRouter()

# In-memory storage (production: use Redis)
policy_engines: Dict[str, PolicyEngine] = {}

class EvaluateActionRequest(BaseModel):
    action: Dict[str, Any]
    state: Dict[str, Any]
    agent_role: str

class CheckInvariantsRequest(BaseModel):
    state: Dict[str, Any]

@router.post("/evaluate-action")
async def evaluate_action(
    request: EvaluateActionRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Evaluate if an action complies with policies"""
    
    logger.info("Evaluating action",
               action_type=request.action.get('type'),
               agent_role=request.agent_role)
    
    # Get or create policy engine (in production, load from blueprint)
    policies = request.state.get('policies', {})
    engine = PolicyEngine(policies)
    
    result = engine.evaluate_action(
        request.action,
        request.state,
        request.agent_role
    )
    
    # Record metrics
    if result.decision == PolicyDecision.DENY:
        metrics.record_metric("policy_denials", 1, {
            "agent_role": request.agent_role,
            "action_type": request.action.get('type')
        })
        for rule in result.violated_rules:
            metrics.record_policy_violation("unknown_run", rule)
    
    elif result.decision == PolicyDecision.ESCALATE:
        metrics.record_metric("policy_escalations", 1, {
            "agent_role": request.agent_role,
            "action_type": request.action.get('type')
        })
    
    return {
        "decision": result.decision.value,
        "reason": result.reason,
        "violated_rules": result.violated_rules
    }

@router.post("/check-invariants")
async def check_invariants(
    request: CheckInvariantsRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Check if state violates invariants"""
    
    policies = request.state.get('policies', {})
    engine = PolicyEngine(policies)
    
    violations = engine.check_invariants(request.state)
    
    if violations:
        logger.warning("Invariant violations detected",
                      violations=violations,
                      state_hash=request.state.get('hash'))
        
        for violation in violations:
            metrics.record_policy_violation("unknown_run", violation)
    
    return {
        "violations": violations,
        "is_valid": len(violations) == 0
    }

@router.get("/policy-rules")
async def get_policy_rules(
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Get available policy rules"""
    
    return {
        "rules": [
            {
                "name": "spend_limit",
                "description": "Monthly spending limit",
                "type": "hard_constraint"
            },
            {
                "name": "max_percent_change",
                "description": "Maximum percentage change for pricing/headcount",
                "type": "hard_constraint"
            },
            {
                "name": "hiring_velocity",
                "description": "Maximum hiring rate per period",
                "type": "hard_constraint"
            },
            {
                "name": "approval_threshold",
                "description": "Financial threshold requiring approval",
                "type": "approval_gate"
            },
            {
                "name": "risk_appetite",
                "description": "Maximum acceptable risk score",
                "type": "approval_gate"
            },
            {
                "name": "min_runway",
                "description": "Minimum runway in months",
                "type": "invariant"
            },
            {
                "name": "min_service_level",
                "description": "Minimum service level percentage",
                "type": "invariant"
            }
        ]
    }
