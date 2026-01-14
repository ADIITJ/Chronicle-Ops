from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ..shared.auth import get_current_user, AuthContext
from ..shared.database import get_db_dependency
from ..shared.models import (
    CompanyBlueprint, EventTimeline, AgentConfig,
    CompanyBlueprintSchema, AgentConfigSchema
)
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

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

@router.post("/blueprints", status_code=status.HTTP_201_CREATED)
async def create_blueprint(
    request: CreateBlueprintRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Create company blueprint"""
    
    # Check for duplicate name (idempotency)
    blueprint: CompanyBlueprintSchema,
    request: Request,
    db: Session = Depends(get_db_dependency) # Changed get_db to get_db_dependency
):
    """Create a new company blueprint with idempotency support"""
    try:
        # Check for idempotency key
        idempotency_key = request.headers.get("X-Idempotency-Key")
        
        if idempotency_key:
            # Check if this request was already processed
            existing = db.query(CompanyBlueprint).filter(
                CompanyBlueprint.name == blueprint.name
            ).first()
            
            if existing:
                # Return existing blueprint (idempotent)
                return {
                    "id": existing.id,
                    "name": existing.name,
                    "industry": existing.industry,
                    "created_at": existing.created_at.isoformat(),
                    "message": "Blueprint already exists (idempotent)"
                }
        
        # Create new blueprint
        db_blueprint = CompanyBlueprint(
            id=str(uuid.uuid4()),
            tenant_id="default-tenant",  # TODO: Get from auth
            name=blueprint.name,
            industry=blueprint.industry.value,
            initial_conditions=blueprint.initial_conditions.dict(),
            constraints=blueprint.constraints.dict(),
            policies=blueprint.policies.dict(),
            market_exposure=blueprint.market_exposure,
            created_by=None  # TODO: Get from auth
        )
        
        db.add(db_blueprint)
        db.commit()
        db.refresh(db_blueprint)
        
        return {
            "id": db_blueprint.id,
            "name": db_blueprint.name,
            "industry": db_blueprint.industry,
            "created_at": db_blueprint.created_at.isoformat(),
            "message": "Blueprint created successfully"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blueprints")
async def list_blueprints(
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """List all blueprints for tenant"""
    blueprints = db.query(CompanyBlueprint).filter(
        CompanyBlueprint.tenant_id == auth.tenant_id
    ).all()
    
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

@router.get("/blueprints/{blueprint_id}")
async def get_blueprint(
    blueprint_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Get blueprint by ID"""
    blueprint = db.query(CompanyBlueprint).filter(
        CompanyBlueprint.id == blueprint_id
    ).first()
    
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    if not auth.can_read(blueprint.tenant_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": blueprint.id,
        "name": blueprint.name,
        "industry": blueprint.industry,
        "initial_conditions": blueprint.initial_conditions,
        "constraints": blueprint.constraints,
        "policies": blueprint.policies,
        "market_exposure": blueprint.market_exposure,
        "version": blueprint.version,
        "created_at": blueprint.created_at.isoformat()
    }

@router.post("/timelines", status_code=status.HTTP_201_CREATED)
async def create_timeline(
    request: CreateTimelineRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Create event timeline"""
    
    # Check for duplicate
    existing = db.query(EventTimeline).filter(
        EventTimeline.tenant_id == auth.tenant_id,
        EventTimeline.name == request.name,
        EventTimeline.version == 1
    ).first()
    
    if existing:
        return {"id": existing.id, "message": "Timeline already exists"}
    
    timeline = EventTimeline(
        tenant_id=auth.tenant_id,
        name=request.name,
        start_date=request.start_date,
        end_date=request.end_date,
        events=request.events,
        created_by=auth.user_id
    )
    
    db.add(timeline)
    db.commit()
    db.refresh(timeline)
    
    return {"id": timeline.id, "version": timeline.version}

@router.get("/timelines")
async def list_timelines(
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """List all timelines for tenant"""
    timelines = db.query(EventTimeline).filter(
        EventTimeline.tenant_id == auth.tenant_id
    ).all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "start_date": t.start_date.isoformat(),
            "end_date": t.end_date.isoformat(),
            "version": t.version,
            "created_at": t.created_at.isoformat()
        }
        for t in timelines
    ]

@router.post("/agent-configs", status_code=status.HTTP_201_CREATED)
async def create_agent_config(
    request: CreateAgentConfigRequest,
    auth: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db_dependency)
):
    """Create agent configuration"""
    
    # Check for duplicate
    existing = db.query(AgentConfig).filter(
        AgentConfig.tenant_id == auth.tenant_id,
        AgentConfig.name == request.name,
        AgentConfig.version == 1
    ).first()
    
    if existing:
        return {"id": existing.id, "message": "Agent config already exists"}
    
    config = AgentConfig(
        tenant_id=auth.tenant_id,
        name=request.name,
        agents=request.agents,
        created_by=auth.user_id
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return {"id": config.id, "version": config.version}
