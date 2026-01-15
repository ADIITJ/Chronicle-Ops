from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

# Simplified request models without auth dependencies
class CreateBlueprintRequest(BaseModel):
    name: str
    industry: str
    initial_conditions: dict
    constraints: dict
    policies: dict
    market_exposure: dict

class CreateTimelineRequest(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    events: List[dict]

class CreateAgentConfigRequest(BaseModel):
    name: str
    agents: List[dict]

def get_db():
    from ..shared.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/blueprints", status_code=status.HTTP_201_CREATED)
async def create_blueprint(
    request: CreateBlueprintRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Create company blueprint with idempotency"""
    from ..shared.models import CompanyBlueprint
    
    idempotency_key = req.headers.get("X-Idempotency-Key")
    
    try:
        # Check for existing blueprint
        existing = db.query(CompanyBlueprint).filter(
            CompanyBlueprint.name == request.name
        ).first()
        
        if existing:
            return {
                "id": existing.id,
                "name": existing.name,
                "industry": existing.industry,
                "created_at": existing.created_at.isoformat(),
                "message": "Blueprint already exists"
            }
        
        # Create new blueprint
        blueprint = CompanyBlueprint(
            id=str(uuid.uuid4()),
            tenant_id="default-tenant",
            version=1,
            name=request.name,
            industry=request.industry,
            initial_conditions=request.initial_conditions,
            constraints=request.constraints,
            policies=request.policies,
            market_exposure=request.market_exposure,
            created_by=None
        )
        
        db.add(blueprint)
        db.commit()
        db.refresh(blueprint)
        
        return {
            "id": blueprint.id,
            "name": blueprint.name,
            "industry": blueprint.industry,
            "version": blueprint.version,
            "created_at": blueprint.created_at.isoformat()
        }
    
    except IntegrityError as e:
        db.rollback()
        # Race condition - blueprint created between check and insert
        existing = db.query(CompanyBlueprint).filter(
            CompanyBlueprint.name == request.name
        ).first()
        if existing:
            return {
                "id": existing.id,
                "name": existing.name,
                "industry": existing.industry,
                "created_at": existing.created_at.isoformat(),
                "message": "Blueprint already exists"
            }
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blueprints")
async def list_blueprints(db: Session = Depends(get_db)):
    """List all blueprints"""
    from ..shared.models import CompanyBlueprint
    
    blueprints = db.query(CompanyBlueprint).all()
    
    return [
        {
            "id": b.id,
            "name": b.name,
            "industry": b.industry,
            "version": b.version,
            "created_at": b.created_at.isoformat()
        }
        for b in blueprints
    ]

@router.post("/timelines", status_code=status.HTTP_201_CREATED)
async def create_timeline(
    request: CreateTimelineRequest,
    db: Session = Depends(get_db)
):
    """Create event timeline with idempotency"""
    from ..shared.models import EventTimeline
    
    try:
        existing = db.query(EventTimeline).filter(
            EventTimeline.name == request.name
        ).first()
        
        if existing:
            return {"id": existing.id, "message": "Timeline already exists"}
        
        timeline = EventTimeline(
            id=str(uuid.uuid4()),
            tenant_id="default-tenant",
            version=1,
            name=request.name,
            start_date=request.start_date,
            end_date=request.end_date,
            events=request.events,
            created_by=None
        )
        
        db.add(timeline)
        db.commit()
        db.refresh(timeline)
        
        return {"id": timeline.id, "version": timeline.version}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent-configs", status_code=status.HTTP_201_CREATED)
async def create_agent_config(
    request: CreateAgentConfigRequest,
    db: Session = Depends(get_db)
):
    """Create agent configuration with idempotency"""
    from ..shared.models import AgentConfig
    
    try:
        existing = db.query(AgentConfig).filter(
            AgentConfig.name == request.name
        ).first()
        
        if existing:
            return {"id": existing.id, "message": "Agent config already exists"}
        
        config = AgentConfig(
            id=str(uuid.uuid4()),
            tenant_id="default-tenant",
            version=1,
            name=request.name,
            agents=request.agents,
            created_by=None
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        return {"id": config.id, "version": config.version}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
