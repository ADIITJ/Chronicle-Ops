from typing import Dict, Any
from ..simulation.state import CompanyState

class D2CModel:
    """D2C industry model: demand → fulfillment → returns"""
    
    @staticmethod
    def update_state(state: CompanyState, days_elapsed: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate D2C-specific state updates"""
        
        # Demand forecast
        base_demand = params.get('base_demand', 1000)
        seasonality = params.get('seasonality_factor', 1.0)
        demand = base_demand * seasonality
        
        # Inventory and fulfillment
        inventory_level = state.inventory.get('default', 0)
        fulfilled = min(demand, inventory_level)
        stockout = max(0, demand - inventory_level)
        
        # Revenue
        avg_order_value = params.get('avg_order_value', 100)
        revenue_monthly = fulfilled * avg_order_value * (30 / days_elapsed)
        
        # Returns
        return_rate = params.get('return_rate', 0.1)
        returns = fulfilled * return_rate
        net_revenue = revenue_monthly * (1 - return_rate)
        
        # CAC from ads
        ad_spend = params.get('ad_spend', 0)
        orders = fulfilled
        cac = ad_spend / max(orders, 1)
        
        # Inventory update
        new_inventory = inventory_level - fulfilled + returns
        
        return {
            'revenue_monthly': net_revenue,
            'inventory': {'default': new_inventory},
            'backlog': {'default': stockout},
            'cac': {'default': cac},
            'demand': {'default': demand},
            'metadata': {
                'fulfilled': fulfilled,
                'stockout': stockout,
                'return_rate': return_rate,
                'avg_order_value': avg_order_value
            }
        }
    
    @staticmethod
    def get_constraints(blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Get D2C-specific constraints"""
        return {
            'min_inventory_days': 30,
            'max_stockout_rate': 0.05,
            'max_return_rate': 0.15,
            'min_gross_margin': 0.4
        }
