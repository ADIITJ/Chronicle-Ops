from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

def get_db():
    from ..shared.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PolicyCheckRequest(BaseModel):
    action: Dict[str, Any]
    agent_role: str

@router.post("/check")
async def check_policy(
    request: PolicyCheckRequest,
    db: Session = Depends(get_db)
):
    """Check if action complies with policies"""
    return {
        "approved": True,
        "requires_escalation": False,
        "reason": "Auto-approved for MVP"
    }
