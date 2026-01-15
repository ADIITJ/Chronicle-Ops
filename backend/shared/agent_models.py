from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import JSONB
from shared.models import Base
import uuid

class AgentDecision(Base):
    """Stores full agent decision reasoning chains"""
    __tablename__ = "agent_decisions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    tick = Column(Integer, nullable=False)
    agent_role = Column(String(50), nullable=False)
    observations = Column(JSONB, nullable=False)
    reasoning = Column(Text, nullable=True)
    proposed_actions = Column(JSONB, nullable=False)
    approved = Column(Boolean, nullable=False, default=False)
    executed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class MarketState(Base):
    """Tracks population/market metrics over time"""
    __tablename__ = "market_state"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    tick = Column(Integer, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    awareness_level = Column(Float, nullable=False)
    trust_level = Column(Float, nullable=False)
    viral_coefficient = Column(Float, nullable=False)
    market_dynamics = Column(JSONB, nullable=False)
    price_perception = Column(Float, nullable=True)
    quality_perception = Column(Float, nullable=True)
    brand_strength = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class EventResponse(Base):
    """Logs how agents respond to world events"""
    __tablename__ = "event_responses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String, nullable=True)
    tick = Column(Integer, nullable=False)
    agent_role = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_description = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=True)
    actions_taken = Column(JSONB, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
