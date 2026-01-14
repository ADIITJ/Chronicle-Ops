from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random
import json
from .state import CompanyState, StateTransition
from .timelock import TimeLock, InformationContext
from ..shared.models import IndustryTemplate

class SimulationEngine:
    """Deterministic discrete-time simulation engine"""
    
    def __init__(
        self,
        blueprint: Dict[str, Any],
        timeline: Dict[str, Any],
        seed: int,
        tick_days: int = 7,  # Weekly ticks by default
        run_id: Optional[str] = None
    ):
        self.blueprint = blueprint
        self.timeline = timeline
        self.seed = seed
        self.tick_days = tick_days
        self.run_id = run_id or 'test-run'
        self.current_tick = 0
        
        # Initialize RNG with seed for determinism
        self.rng = random.Random(seed)
        
        # Time-lock
        self.timelock = TimeLock()
        self.encrypted_events = self.timelock.encrypt_future_events(
            timeline['events'],
            datetime.fromisoformat(timeline['start_date'])
        )
        
        # State
        self.current_time = datetime.fromisoformat(timeline['start_date'])
        self.end_time = datetime.fromisoformat(timeline['end_date'])
        self.state = self._initialize_state()
        
        # History
        self.state_history: List[CompanyState] = [self.state]
        self.transitions: List[StateTransition] = []
        self.checkpoints: Dict[str, CompanyState] = {}
        
        # Event tracking
        self.active_events: List[Dict[str, Any]] = []
        self.event_history: List[Dict[str, Any]] = []
    
    def _initialize_state(self) -> CompanyState:
        """Create initial state from blueprint"""
        ic = self.blueprint['initial_conditions']
        return CompanyState(
            timestamp=self.current_time,
            version=0,
            cash=ic['cash'],
            revenue_monthly=0.0,
            costs_monthly=ic['monthly_burn'],
            margin=ic.get('margins', {}).get('gross', 0.0),
            headcount=ic['headcount'],
            capacity=ic.get('capacity', {}),
            utilization={},
            demand={},
            pricing=ic.get('pricing', {}),
            cac={},
            churn_rate=0.0,
            inventory={},
            backlog={},
            lead_times={},
            service_level=1.0,
            risk_flags={},
            compliance_score=1.0,
            metadata={'growth_rate': 0.0}
        )
    
    def get_information_context(self) -> Dict[str, Any]:
        """Get time-locked information context for agents"""
        base_context = InformationContext(
            current_time=self.current_time,
            timelock=self.timelock,
            events=self.encrypted_events
        )
        
        # Add active events that agents should be aware of
        return {
            **base_context.__dict__,
            'active_events': self.active_events,
            'recent_events': self.event_history[-5:] if self.event_history else [],
            'current_tick': self.current_tick
        }
    
    def apply_action(self, action: Dict[str, Any], agent_role: Optional[str] = None) -> bool:
        """Apply agent action to state (idempotent if action has unique ID)"""
        
        # Idempotency check
        action_id = action.get('id')
        if action_id:
            # Check if already applied
            for transition in self.transitions:
                if transition.action.get('id') == action_id:
                    return True  # Already applied, idempotent success
        
        # Create new state with action applied
        new_state = self._apply_action_to_state(self.state, action)
        
        # Validate transition
        transition = StateTransition(
            before=self.state,
            after=new_state,
            action=action,
            agent_role=agent_role,
            reason=action.get('reason', '')
        )
        
        if not transition.is_valid():
            return False
        
        # Commit transition
        self.state = new_state
        self.state_history.append(new_state)
        self.transitions.append(transition)
        
        return True
    
    def _apply_action_to_state(self, state: CompanyState, action: Dict[str, Any]) -> CompanyState:
        """Apply action to state and return new state"""
        action_type = action['type']
        params = action.get('params', {})
        
        updates = {'timestamp': self.current_time}
        
        if action_type == 'adjust_hiring':
            delta = params['delta']
            updates['headcount'] = max(0, state.headcount + delta)
            updates['costs_monthly'] = state.costs_monthly + (delta * params.get('cost_per_head', 10000))
        
        elif action_type == 'change_pricing':
            new_pricing = state.pricing.copy()
            for product, price in params.get('pricing', {}).items():
                new_pricing[product] = price
            updates['pricing'] = new_pricing
        
        elif action_type == 'allocate_budget':
            allocation = params.get('allocation', {})
            total = sum(allocation.values())
            if total <= state.cash:
                updates['cash'] = state.cash - total
        
        elif action_type == 'modify_inventory_policy':
            new_inventory = state.inventory.copy()
            for item, quantity in params.get('inventory', {}).items():
                new_inventory[item] = quantity
            updates['inventory'] = new_inventory
        
        elif action_type == 'trigger_cost_cutting':
            reduction = params.get('reduction_percent', 0.1)
            updates['costs_monthly'] = state.costs_monthly * (1 - reduction)
        
        return state.clone(**updates)
    
    def tick(self) -> bool:
        """Advance simulation by one tick"""
        if self.current_time >= self.end_time:
            return False
        
        # Increment tick counter
        self.current_tick += 1
        
        # Advance time
        self.current_time += timedelta(days=self.tick_days)
        
        # Process events at this time
        context = self.get_information_context()
        events = context.get('active_events', []) if isinstance(context, dict) else []
        
        # Clear expired events
        self.active_events = [e for e in self.active_events 
                             if datetime.fromisoformat(e['timestamp']) + timedelta(days=e.get('duration_days', 7)) > self.current_time]
        
        # Add new events
        for event in events:
            event_time = datetime.fromisoformat(event['timestamp'])
            if abs((event_time - self.current_time).days) < self.tick_days:
                self.active_events.append(event)
                self.event_history.append({
                    **event,
                    'activated_at': self.current_time.isoformat(),
                    'tick': self.current_tick
                })
                self._apply_event(event)
        
        # Update state based on time passage
        self._update_state_for_tick()
        
        return True
    
    def _apply_event(self, event: Dict[str, Any]):
        """Apply event impacts to state"""
        impacts = event.get('parameter_impacts', {})
        
        updates = {}
        if 'demand_multiplier' in impacts:
            new_demand = {k: v * impacts['demand_multiplier'] for k, v in self.state.demand.items()}
            updates['demand'] = new_demand
        
        if 'cost_multiplier' in impacts:
            updates['costs_monthly'] = self.state.costs_monthly * impacts['cost_multiplier']
        
        if 'churn_delta' in impacts:
            updates['churn_rate'] = max(0, min(1, self.state.churn_rate + impacts['churn_delta']))
        
        if updates:
            self.state = self.state.clone(timestamp=self.current_time, **updates)
            self.state_history.append(self.state)
    
    def _update_state_for_tick(self):
        """Update state for time passage (revenue, costs, cash flow)"""
        days_fraction = self.tick_days / 30.0
        
        revenue = self.state.revenue_monthly * days_fraction
        costs = self.state.costs_monthly * days_fraction
        net_cash_flow = revenue - costs
        
        new_cash = self.state.cash + net_cash_flow
        
        self.state = self.state.clone(
            timestamp=self.current_time,
            cash=new_cash
        )
        self.state_history.append(self.state)
    
    def create_checkpoint(self, name: str):
        """Save checkpoint for branching"""
        self.checkpoints[name] = self.state
    
    def restore_checkpoint(self, name: str) -> bool:
        """Restore from checkpoint"""
        if name not in self.checkpoints:
            return False
        
        checkpoint_state = self.checkpoints[name]
        self.state = checkpoint_state
        self.current_time = checkpoint_state.timestamp
        
        # Truncate history to checkpoint
        self.state_history = [s for s in self.state_history if s.timestamp <= checkpoint_state.timestamp]
        self.transitions = [t for t in self.transitions if t.before.timestamp <= checkpoint_state.timestamp]
        
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            'current_time': self.current_time.isoformat(),
            'cash': self.state.cash,
            'runway_months': self.state.runway_months,
            'revenue_monthly': self.state.revenue_monthly,
            'costs_monthly': self.state.costs_monthly,
            'margin': self.state.margin,
            'headcount': self.state.headcount,
            'growth_rate': self.state.growth_rate,
            'service_level': self.state.service_level,
            'compliance_score': self.state.compliance_score,
            'state_version': self.state.version
        }
    
    def export_state(self) -> Dict[str, Any]:
        """Export full state for persistence"""
        return {
            'current_time': self.current_time.isoformat(),
            'state': self.state.to_dict(),
            'state_hash': self.state.hash(),
            'metrics': self.get_metrics()
        }
