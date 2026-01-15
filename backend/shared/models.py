from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, Boolean, Float, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
import uuid

Base = declarative_base()

class IndustryTemplate(str, Enum):
    SAAS = "saas"
    D2C = "d2c"
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    FINTECH = "fintech"
    MARKETPLACE = "marketplace"

class RunStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentRole(str, Enum):
    CEO = "ceo"
    CFO = "cfo"
    COO = "coo"
    PRODUCT = "product"
    SALES = "sales"
    RISK = "risk"

# Database Models
class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (Index("idx_user_tenant", "tenant_id"),)

class CompanyBlueprint(Base):
    __tablename__ = "company_blueprints"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    initial_conditions = Column(JSON, nullable=False)
    constraints = Column(JSON, nullable=False)
    policies = Column(JSON, nullable=False)
    market_exposure = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"))
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", "version", name="uq_blueprint_version"),
        Index("idx_blueprint_tenant", "tenant_id"),
    )

class EventTimeline(Base):
    __tablename__ = "event_timelines"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    events = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"))
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", "version", name="uq_timeline_version"),
        Index("idx_timeline_tenant", "tenant_id"),
    )

class AgentConfig(Base):
    __tablename__ = "agent_configs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    name = Column(String, nullable=False)
    agents = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"))
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", "version", name="uq_agent_config_version"),
        Index("idx_agent_config_tenant", "tenant_id"),
    )

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    blueprint_id = Column(String, ForeignKey("company_blueprints.id"), nullable=False)
    timeline_id = Column(String, ForeignKey("event_timelines.id"), nullable=False)
    agent_config_id = Column(String, ForeignKey("agent_configs.id"), nullable=False)
    seed = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default=RunStatus.CREATED.value)
    current_tick = Column(Integer, default=0)
    current_time = Column(DateTime)
    final_state = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
    
    __table_args__ = (
        Index("idx_run_tenant", "tenant_id"),
        Index("idx_run_status", "status"),
    )

class AuditEntry(Base):
    __tablename__ = "audit_entries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("simulation_runs.id"), nullable=False)
    sequence = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    sim_time = Column(DateTime, nullable=False)
    entry_type = Column(String, nullable=False)
    agent_role = Column(String)
    action = Column(JSON)
    state_before = Column(JSON)
    state_after = Column(JSON)
    policy_check = Column(JSON)
    signature = Column(Text, nullable=False)
    prev_signature = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("run_id", "sequence", name="uq_audit_sequence"),
        Index("idx_audit_run", "run_id"),
        Index("idx_audit_sequence", "run_id", "sequence"),
    )

# Pydantic Schemas
class InitialConditions(BaseModel):
    cash: float = Field(gt=0)
    monthly_burn: float = Field(ge=0)
    pricing: Dict[str, float] = Field(default_factory=dict)
    margins: Dict[str, float] = Field(default_factory=dict)
    headcount: int = Field(ge=0)
    capacity: Optional[Dict[str, float]] = None

class Constraints(BaseModel):
    hiring_velocity_max: int = Field(gt=0)
    procurement_lead_time_days: Dict[str, tuple[int, int]]
    working_capital_min: float = Field(ge=0)
    sla_targets: Optional[Dict[str, float]] = None
    compliance_strictness: float = Field(ge=0, le=1)

class Policies(BaseModel):
    spend_limit_monthly: float = Field(gt=0)
    approval_threshold: float = Field(gt=0)
    max_percent_change: Dict[str, float]
    risk_appetite: float = Field(ge=0, le=1)

class CompanyBlueprintSchema(BaseModel):
    name: str
    industry: IndustryTemplate
    initial_conditions: InitialConditions
    constraints: Constraints
    policies: Policies
    market_exposure: Dict[str, Any]

class Event(BaseModel):
    timestamp: datetime
    event_type: str
    severity: float = Field(ge=0, le=1)
    duration_days: int = Field(gt=0)
    affected_areas: List[str]
    signals: List[Dict[str, Any]]
    parameter_impacts: Dict[str, Any]

class AgentDefinition(BaseModel):
    role: AgentRole
    objectives: Dict[str, float]
    permissions: List[str]
    approval_threshold: float
    risk_appetite: float = Field(ge=0, le=1)

class AgentConfigSchema(BaseModel):
    name: str
    agents: List[AgentDefinition]
