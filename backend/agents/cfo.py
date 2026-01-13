from typing import Dict, Any, List
from .base import BaseAgent, Tool

class CFOAgent(BaseAgent):
    """CFO Agent: budget, runway, pricing constraints, risk limits"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            role="cfo",
            objectives=config.get('objectives', {
                'profitability': 0.5,
                'runway': 0.3,
                'risk_management': 0.2
            }),
            permissions=[
                'allocate_budget',
                'modify_pricing',
                'modify_costs',
                'approve_financial'
            ],
            approval_threshold=config.get('approval_threshold', 500000),
            risk_appetite=config.get('risk_appetite', 0.3)
        )
    
    def _register_tools(self) -> List[Tool]:
        from .tools import get_tools_for_permissions
        tool_defs = get_tools_for_permissions(self.permissions)
        return [
            Tool(
                name=t['name'],
                description=t['description'],
                parameters=t['parameters'],
                handler=lambda x: x
            )
            for t in tool_defs
        ]
