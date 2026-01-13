from typing import Dict, Any, List
from enum import Enum

class PolicyDecision(str, Enum):
    APPROVE = "approve"
    DENY = "deny"
    ESCALATE = "escalate"

class PolicyResult:
    def __init__(self, decision: PolicyDecision, reason: str, violated_rules: List[str] = None):
        self.decision = decision
        self.reason = reason
        self.violated_rules = violated_rules or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision': self.decision.value,
            'reason': self.reason,
            'violated_rules': self.violated_rules
        }

class PolicyEngine:
    """Centralized policy enforcement"""
    
    def __init__(self, policies: Dict[str, Any]):
        self.policies = policies
    
    def evaluate_action(
        self,
        action: Dict[str, Any],
        state: Dict[str, Any],
        agent_role: str
    ) -> PolicyResult:
        """Evaluate if action is allowed under policies"""
        
        action_type = action.get('type')
        params = action.get('params', {})
        
        violated = []
        
        # Check spend limits
        if action_type == 'allocate_budget':
            total_spend = sum(params.get('allocation', {}).values())
            limit = self.policies.get('spend_limit_monthly', float('inf'))
            if total_spend > limit:
                violated.append(f"spend_limit: {total_spend} > {limit}")
        
        # Check percent change limits
        if action_type == 'change_pricing':
            max_change = self.policies.get('max_percent_change', {}).get('pricing', 0.2)
            for product, new_price in params.get('pricing', {}).items():
                old_price = state.get('pricing', {}).get(product, new_price)
                if old_price > 0:
                    change = abs(new_price - old_price) / old_price
                    if change > max_change:
                        violated.append(f"pricing_change: {change:.1%} > {max_change:.1%} for {product}")
        
        # Check hiring velocity
        if action_type == 'adjust_hiring':
            delta = abs(params.get('delta', 0))
            max_velocity = self.policies.get('constraints', {}).get('hiring_velocity_max', 10)
            if delta > max_velocity:
                violated.append(f"hiring_velocity: {delta} > {max_velocity}")
        
        # Check approval thresholds
        estimated_impact = action.get('estimated_impact', 0)
        approval_threshold = self.policies.get('approval_threshold', 100000)
        needs_approval = estimated_impact > approval_threshold
        
        # Check risk appetite
        risk_score = action.get('risk_score', 0)
        risk_appetite = self.policies.get('risk_appetite', 0.5)
        too_risky = risk_score > risk_appetite
        
        # Make decision
        if violated:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Policy violations: {', '.join(violated)}",
                violated_rules=violated
            )
        
        if needs_approval or too_risky:
            return PolicyResult(
                decision=PolicyDecision.ESCALATE,
                reason=f"Requires approval (impact: ${estimated_impact:,.0f}, risk: {risk_score:.2f})"
            )
        
        return PolicyResult(
            decision=PolicyDecision.APPROVE,
            reason="Action complies with all policies"
        )
    
    def check_invariants(self, state: Dict[str, Any]) -> List[str]:
        """Check if state violates invariants"""
        violations = []
        
        # Cash cannot be negative
        if state.get('cash', 0) < 0:
            violations.append("cash_negative")
        
        # Runway must be above minimum
        min_runway = self.policies.get('min_runway_months', 3)
        runway = state.get('runway_months', 0)
        if runway < min_runway:
            violations.append(f"runway_too_low: {runway:.1f} < {min_runway}")
        
        # Service level must meet SLA
        min_service_level = self.policies.get('constraints', {}).get('sla_targets', {}).get('min', 0.95)
        service_level = state.get('service_level', 1.0)
        if service_level < min_service_level:
            violations.append(f"service_level_below_sla: {service_level:.2%} < {min_service_level:.2%}")
        
        return violations
