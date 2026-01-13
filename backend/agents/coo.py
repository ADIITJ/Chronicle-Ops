from typing import Dict, Any, List
from .base import BaseAgent, Tool

class COOAgent(BaseAgent):
    """COO Agent: inventory, lead times, service levels, supply chain"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            role="coo",
            objectives=config.get('objectives', {
                'service_level': 0.4,
                'efficiency': 0.3,
                'cost_optimization': 0.3
            }),
            permissions=[
                'modify_inventory',
                'modify_suppliers',
                'modify_capacity',
                'approve_operations'
            ],
            approval_threshold=config.get('approval_threshold', 250000),
            risk_appetite=config.get('risk_appetite', 0.4)
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
