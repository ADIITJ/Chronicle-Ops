from typing import Dict, Any, List
from .base import BaseAgent, Tool

class CEOAgent(BaseAgent):
    """CEO Agent: strategy, conflict resolution, high-impact approvals"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            role="ceo",
            objectives=config.get('objectives', {
                'growth': 0.3,
                'profitability': 0.3,
                'resilience': 0.4
            }),
            permissions=[
                'modify_headcount',
                'modify_pricing',
                'allocate_budget',
                'modify_expansion',
                'approve_all'
            ],
            approval_threshold=config.get('approval_threshold', 1000000),
            risk_appetite=config.get('risk_appetite', 0.5)
        )
    
    def _register_tools(self) -> List[Tool]:
        from .tools import get_tools_for_permissions
        tool_defs = get_tools_for_permissions(self.permissions)
        return [
            Tool(
                name=t['name'],
                description=t['description'],
                parameters=t['parameters'],
                handler=lambda x: x  # Placeholder
            )
            for t in tool_defs
        ]
