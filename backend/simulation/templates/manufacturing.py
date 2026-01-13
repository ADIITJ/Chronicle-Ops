from typing import Dict, Any
import random
from ..simulation.state import CompanyState

class ManufacturingModel:
    """Manufacturing/logistics model: lead times, supplier reliability, safety stock"""
    
    @staticmethod
    def update_state(state: CompanyState, days_elapsed: int, params: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
        """Calculate manufacturing-specific state updates"""
        
        # Demand
        demand = params.get('demand', 1000)
        
        # Lead time simulation (stochastic)
        base_lead_time = params.get('base_lead_time_days', 30)
        lead_time_std = params.get('lead_time_std_days', 5)
        actual_lead_time = max(1, int(rng.gauss(base_lead_time, lead_time_std)))
        
        # Supplier reliability
        supplier_reliability = params.get('supplier_reliability', 0.95)
        supplier_delivers = rng.random() < supplier_reliability
        
        # Inventory
        safety_stock = params.get('safety_stock', 500)
        current_inventory = state.inventory.get('default', safety_stock)
        
        # Fulfillment
        if supplier_delivers:
            replenishment = params.get('order_quantity', 1000)
            current_inventory += replenishment
        
        fulfilled = min(demand, current_inventory)
        current_inventory -= fulfilled
        backlog = max(0, demand - fulfilled)
        
        # Service level
        service_level = fulfilled / max(demand, 1)
        
        # Expedite costs (if inventory below safety stock)
        expedite_cost = 0
        if current_inventory < safety_stock:
            shortage = safety_stock - current_inventory
            expedite_cost = shortage * params.get('expedite_cost_per_unit', 10)
        
        # Revenue
        unit_price = params.get('unit_price', 100)
        revenue_monthly = fulfilled * unit_price * (30 / days_elapsed)
        
        # Costs
        cogs = fulfilled * params.get('cogs_per_unit', 60)
        holding_cost = current_inventory * params.get('holding_cost_per_unit', 1)
        total_costs = cogs + holding_cost + expedite_cost
        
        return {
            'revenue_monthly': revenue_monthly,
            'costs_monthly': state.costs_monthly + (total_costs * (30 / days_elapsed)),
            'inventory': {'default': current_inventory},
            'backlog': {'default': backlog},
            'lead_times': {'default': actual_lead_time},
            'service_level': service_level,
            'metadata': {
                'fulfilled': fulfilled,
                'expedite_cost': expedite_cost,
                'supplier_reliability': supplier_reliability,
                'safety_stock': safety_stock
            }
        }
    
    @staticmethod
    def get_constraints(blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Get manufacturing-specific constraints"""
        return {
            'min_service_level': 0.95,
            'max_lead_time_days': 90,
            'min_supplier_reliability': 0.90,
            'max_inventory_turns': 12
        }
