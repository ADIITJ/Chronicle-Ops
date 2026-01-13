from typing import Dict, Any, List, Tuple
from datetime import datetime
import copy
from .engine import SimulationEngine
from ..shared.observability import logger

class CounterfactualEngine:
    """Production-grade counterfactual evaluation and regret scoring"""
    
    def __init__(self, simulation: SimulationEngine):
        self.simulation = simulation
    
    def generate_alternatives(
        self,
        current_action: Dict[str, Any],
        state: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate feasible alternative actions"""
        
        action_type = current_action.get('type')
        params = current_action.get('params', {})
        alternatives = []
        
        if action_type == 'adjust_hiring':
            delta = params.get('delta', 0)
            max_velocity = constraints.get('hiring_velocity_max', 10)
            
            # Alternative: no hiring change
            alternatives.append({
                'type': 'adjust_hiring',
                'params': {'delta': 0, 'cost_per_head': params.get('cost_per_head', 10000)},
                'reason': 'Maintain current headcount'
            })
            
            # Alternative: opposite direction (if feasible)
            if delta > 0:
                alternatives.append({
                    'type': 'adjust_hiring',
                    'params': {'delta': -min(delta, max_velocity), 'cost_per_head': params.get('cost_per_head', 10000)},
                    'reason': 'Reduce headcount instead'
                })
            elif delta < 0:
                alternatives.append({
                    'type': 'adjust_hiring',
                    'params': {'delta': min(abs(delta), max_velocity), 'cost_per_head': params.get('cost_per_head', 10000)},
                    'reason': 'Increase headcount instead'
                })
            
            # Alternative: moderate change
            if abs(delta) > 2:
                alternatives.append({
                    'type': 'adjust_hiring',
                    'params': {'delta': int(delta * 0.5), 'cost_per_head': params.get('cost_per_head', 10000)},
                    'reason': 'More conservative hiring change'
                })
        
        elif action_type == 'change_pricing':
            pricing = params.get('pricing', {})
            max_change = constraints.get('max_percent_change', {}).get('pricing', 0.2)
            
            # Alternative: no pricing change
            alternatives.append({
                'type': 'change_pricing',
                'params': {'pricing': state.get('pricing', {})},
                'reason': 'Maintain current pricing'
            })
            
            # Alternative: smaller price change
            moderate_pricing = {}
            for product, new_price in pricing.items():
                old_price = state.get('pricing', {}).get(product, new_price)
                change = (new_price - old_price) * 0.5
                moderate_pricing[product] = old_price + change
            
            alternatives.append({
                'type': 'change_pricing',
                'params': {'pricing': moderate_pricing},
                'reason': 'More conservative pricing adjustment'
            })
        
        elif action_type == 'allocate_budget':
            allocation = params.get('allocation', {})
            
            # Alternative: no budget change
            alternatives.append({
                'type': 'allocate_budget',
                'params': {'allocation': {}},
                'reason': 'Maintain current budget allocation'
            })
            
            # Alternative: reduced spending
            reduced_allocation = {k: v * 0.7 for k, v in allocation.items()}
            alternatives.append({
                'type': 'allocate_budget',
                'params': {'allocation': reduced_allocation},
                'reason': 'More conservative spending'
            })
        
        elif action_type == 'trigger_cost_cutting':
            reduction = params.get('reduction_percent', 0.1)
            
            # Alternative: no cost cutting
            alternatives.append({
                'type': 'trigger_cost_cutting',
                'params': {'reduction_percent': 0, 'areas': []},
                'reason': 'Avoid cost cutting'
            })
            
            # Alternative: less aggressive cutting
            if reduction > 0.05:
                alternatives.append({
                    'type': 'trigger_cost_cutting',
                    'params': {'reduction_percent': reduction * 0.5, 'areas': params.get('areas', [])},
                    'reason': 'Less aggressive cost reduction'
                })
        
        return alternatives
    
    def simulate_forward(
        self,
        action: Dict[str, Any],
        checkpoint_state: Any,
        ticks: int = 10
    ) -> Dict[str, Any]:
        """Simulate forward from checkpoint with given action"""
        
        # Create simulation copy
        sim_copy = copy.deepcopy(self.simulation)
        sim_copy.state = checkpoint_state
        
        # Apply action
        sim_copy.apply_action(action)
        
        # Simulate forward
        for _ in range(ticks):
            can_continue = sim_copy.tick()
            if not can_continue:
                break
        
        # Return final metrics
        return sim_copy.get_metrics()
    
    def compute_regret(
        self,
        chosen_action: Dict[str, Any],
        alternatives: List[Dict[str, Any]],
        checkpoint_state: Any,
        primary_metric: str = 'cash',
        ticks: int = 10
    ) -> Dict[str, Any]:
        """Compute regret: best alternative - chosen outcome"""
        
        logger.info("Computing counterfactual regret", 
                   action_type=chosen_action.get('type'),
                   num_alternatives=len(alternatives))
        
        # Simulate chosen action
        chosen_outcome = self.simulate_forward(chosen_action, checkpoint_state, ticks)
        chosen_value = chosen_outcome.get(primary_metric, 0)
        
        # Simulate alternatives
        alternative_outcomes = []
        for alt_action in alternatives:
            outcome = self.simulate_forward(alt_action, checkpoint_state, ticks)
            alternative_outcomes.append({
                'action': alt_action,
                'outcome': outcome,
                'value': outcome.get(primary_metric, 0)
            })
        
        # Find best alternative
        best_alternative = max(alternative_outcomes, key=lambda x: x['value'])
        best_value = best_alternative['value']
        
        # Compute regret
        regret = best_value - chosen_value
        regret_percent = (regret / abs(chosen_value)) * 100 if chosen_value != 0 else 0
        
        logger.info("Regret computed",
                   chosen_value=chosen_value,
                   best_value=best_value,
                   regret=regret,
                   regret_percent=regret_percent)
        
        return {
            'chosen_action': chosen_action,
            'chosen_outcome': chosen_outcome,
            'chosen_value': chosen_value,
            'best_alternative': best_alternative,
            'best_value': best_value,
            'regret': regret,
            'regret_percent': regret_percent,
            'all_alternatives': alternative_outcomes
        }
    
    def evaluate_decision_point(
        self,
        action: Dict[str, Any],
        state: Dict[str, Any],
        constraints: Dict[str, Any],
        checkpoint_state: Any,
        primary_metric: str = 'cash'
    ) -> Dict[str, Any]:
        """Full counterfactual evaluation at a decision point"""
        
        # Generate alternatives
        alternatives = self.generate_alternatives(action, state, constraints)
        
        if not alternatives:
            logger.warning("No alternatives generated for action", action_type=action.get('type'))
            return {
                'regret': 0,
                'alternatives_count': 0
            }
        
        # Compute regret
        regret_analysis = self.compute_regret(
            action,
            alternatives,
            checkpoint_state,
            primary_metric
        )
        
        return regret_analysis
