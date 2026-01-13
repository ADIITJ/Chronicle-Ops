from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from copy import deepcopy
import hashlib
import json

@dataclass
class CompanyState:
    """Immutable snapshot of company state at a point in time"""
    timestamp: datetime
    version: int
    
    # Financial
    cash: float
    revenue_monthly: float
    costs_monthly: float
    margin: float
    
    # Operations
    headcount: int
    capacity: Dict[str, float] = field(default_factory=dict)
    utilization: Dict[str, float] = field(default_factory=dict)
    
    # Market
    demand: Dict[str, float] = field(default_factory=dict)
    pricing: Dict[str, float] = field(default_factory=dict)
    cac: Dict[str, float] = field(default_factory=dict)
    churn_rate: float = 0.0
    
    # Supply Chain (for manufacturing/logistics)
    inventory: Dict[str, float] = field(default_factory=dict)
    backlog: Dict[str, float] = field(default_factory=dict)
    lead_times: Dict[str, int] = field(default_factory=dict)
    service_level: float = 1.0
    
    # Risk
    risk_flags: Dict[str, Any] = field(default_factory=dict)
    compliance_score: float = 1.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def clone(self, **updates) -> 'CompanyState':
        """Create new state with updates (immutable pattern)"""
        state_dict = {
            'timestamp': self.timestamp,
            'version': self.version + 1,
            'cash': self.cash,
            'revenue_monthly': self.revenue_monthly,
            'costs_monthly': self.costs_monthly,
            'margin': self.margin,
            'headcount': self.headcount,
            'capacity': deepcopy(self.capacity),
            'utilization': deepcopy(self.utilization),
            'demand': deepcopy(self.demand),
            'pricing': deepcopy(self.pricing),
            'cac': deepcopy(self.cac),
            'churn_rate': self.churn_rate,
            'inventory': deepcopy(self.inventory),
            'backlog': deepcopy(self.backlog),
            'lead_times': deepcopy(self.lead_times),
            'service_level': self.service_level,
            'risk_flags': deepcopy(self.risk_flags),
            'compliance_score': self.compliance_score,
            'metadata': deepcopy(self.metadata)
        }
        state_dict.update(updates)
        return CompanyState(**state_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'cash': self.cash,
            'revenue_monthly': self.revenue_monthly,
            'costs_monthly': self.costs_monthly,
            'margin': self.margin,
            'headcount': self.headcount,
            'capacity': self.capacity,
            'utilization': self.utilization,
            'demand': self.demand,
            'pricing': self.pricing,
            'cac': self.cac,
            'churn_rate': self.churn_rate,
            'inventory': self.inventory,
            'backlog': self.backlog,
            'lead_times': self.lead_times,
            'service_level': self.service_level,
            'risk_flags': self.risk_flags,
            'compliance_score': self.compliance_score,
            'metadata': self.metadata
        }
    
    def hash(self) -> str:
        """Deterministic hash for verification"""
        state_json = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    @property
    def runway_months(self) -> float:
        """Calculate runway in months"""
        if self.costs_monthly <= 0:
            return float('inf')
        return self.cash / self.costs_monthly
    
    @property
    def growth_rate(self) -> float:
        """Monthly growth rate"""
        return self.metadata.get('growth_rate', 0.0)

class StateTransition:
    """Represents a state change with full audit trail"""
    def __init__(
        self,
        before: CompanyState,
        after: CompanyState,
        action: Dict[str, Any],
        agent_role: Optional[str] = None,
        reason: str = ""
    ):
        self.before = before
        self.after = after
        self.action = action
        self.agent_role = agent_role
        self.reason = reason
        self.timestamp = datetime.utcnow()
    
    def is_valid(self) -> bool:
        """Verify transition maintains invariants"""
        # Cash cannot go negative
        if self.after.cash < 0:
            return False
        
        # Headcount cannot go negative
        if self.after.headcount < 0:
            return False
        
        # Version must increment
        if self.after.version != self.before.version + 1:
            return False
        
        # Timestamp must advance
        if self.after.timestamp < self.before.timestamp:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'before_hash': self.before.hash(),
            'after_hash': self.after.hash(),
            'action': self.action,
            'agent_role': self.agent_role,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat()
        }
