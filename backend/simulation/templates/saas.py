from typing import Dict, Any
from ..simulation.state import CompanyState

class SaaSModel:
    """SaaS industry-specific model: pipeline → bookings → revenue"""
    
    @staticmethod
    def update_state(state: CompanyState, days_elapsed: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate SaaS-specific state updates"""
        
        # Pipeline dynamics
        pipeline_value = params.get('pipeline_value', 0)
        conversion_rate = params.get('conversion_rate', 0.2)
        sales_cycle_days = params.get('sales_cycle_days', 60)
        
        # Bookings
        bookings = pipeline_value * conversion_rate * (days_elapsed / sales_cycle_days)
        
        # Revenue recognition (assume monthly)
        arr = params.get('arr', 0)
        mrr = arr / 12
        revenue_monthly = mrr
        
        # Churn impact
        churn_rate = state.churn_rate
        revenue_monthly *= (1 - churn_rate)
        
        # CAC dynamics
        marketing_spend = params.get('marketing_spend', 0)
        new_customers = params.get('new_customers', 1)
        cac = marketing_spend / max(new_customers, 1)
        
        # Growth
        growth_rate = (bookings / max(arr, 1)) if arr > 0 else 0
        
        return {
            'revenue_monthly': revenue_monthly,
            'cac': {'default': cac},
            'metadata': {
                'growth_rate': growth_rate,
                'arr': arr,
                'mrr': mrr,
                'bookings': bookings,
                'pipeline_value': pipeline_value
            }
        }
    
    @staticmethod
    def get_constraints(blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Get SaaS-specific constraints"""
        return {
            'min_runway_months': 6,
            'max_cac_payback_months': 12,
            'min_gross_margin': 0.7,
            'max_burn_multiple': 2.0  # Burn multiple = net burn / net new ARR
        }
