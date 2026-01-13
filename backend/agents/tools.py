from typing import Dict, Any, Callable
from pydantic import BaseModel, Field

class ActionParams(BaseModel):
    """Base class for action parameters"""
    pass

class AdjustHiringParams(ActionParams):
    delta: int = Field(description="Change in headcount (positive or negative)")
    cost_per_head: float = Field(default=10000, description="Monthly cost per employee")
    justification: str = Field(description="Reason for hiring change")

class ChangePricingParams(ActionParams):
    pricing: Dict[str, float] = Field(description="New pricing by product/tier")
    justification: str = Field(description="Reason for pricing change")

class AllocateBudgetParams(ActionParams):
    allocation: Dict[str, float] = Field(description="Budget allocation by category")
    justification: str = Field(description="Reason for allocation")

class ModifyInventoryPolicyParams(ActionParams):
    inventory: Dict[str, float] = Field(description="New inventory levels by item")
    justification: str = Field(description="Reason for inventory change")

class SwitchSupplierParams(ActionParams):
    supplier_id: str = Field(description="New supplier identifier")
    justification: str = Field(description="Reason for supplier change")

class TriggerCostCuttingParams(ActionParams):
    reduction_percent: float = Field(ge=0, le=0.5, description="Cost reduction percentage")
    areas: list[str] = Field(description="Areas to cut costs")
    justification: str = Field(description="Reason for cost cutting")

class PauseExpansionParams(ActionParams):
    region: str = Field(description="Region to pause expansion")
    duration_months: int = Field(gt=0, description="Duration of pause")
    justification: str = Field(description="Reason for pausing expansion")

# Tool definitions
TOOLS = {
    'adjust_hiring': {
        'name': 'adjust_hiring',
        'description': 'Adjust company headcount within hiring velocity constraints',
        'parameters': {
            'type': 'object',
            'properties': {
                'delta': {'type': 'integer', 'description': 'Change in headcount'},
                'cost_per_head': {'type': 'number', 'description': 'Monthly cost per employee'},
                'justification': {'type': 'string', 'description': 'Reason for change'}
            },
            'required': ['delta', 'justification']
        },
        'permissions_required': ['modify_headcount']
    },
    
    'change_pricing': {
        'name': 'change_pricing',
        'description': 'Modify product pricing within configured boundaries',
        'parameters': {
            'type': 'object',
            'properties': {
                'pricing': {
                    'type': 'object',
                    'description': 'New pricing by product',
                    'additionalProperties': {'type': 'number'}
                },
                'justification': {'type': 'string', 'description': 'Reason for change'}
            },
            'required': ['pricing', 'justification']
        },
        'permissions_required': ['modify_pricing']
    },
    
    'allocate_budget': {
        'name': 'allocate_budget',
        'description': 'Allocate budget across channels/categories',
        'parameters': {
            'type': 'object',
            'properties': {
                'allocation': {
                    'type': 'object',
                    'description': 'Budget by category',
                    'additionalProperties': {'type': 'number'}
                },
                'justification': {'type': 'string', 'description': 'Reason for allocation'}
            },
            'required': ['allocation', 'justification']
        },
        'permissions_required': ['allocate_budget']
    },
    
    'modify_inventory_policy': {
        'name': 'modify_inventory_policy',
        'description': 'Adjust inventory levels and reorder points',
        'parameters': {
            'type': 'object',
            'properties': {
                'inventory': {
                    'type': 'object',
                    'description': 'Inventory levels by item',
                    'additionalProperties': {'type': 'number'}
                },
                'justification': {'type': 'string', 'description': 'Reason for change'}
            },
            'required': ['inventory', 'justification']
        },
        'permissions_required': ['modify_inventory']
    },
    
    'switch_supplier': {
        'name': 'switch_supplier',
        'description': 'Change supplier for procurement',
        'parameters': {
            'type': 'object',
            'properties': {
                'supplier_id': {'type': 'string', 'description': 'New supplier ID'},
                'justification': {'type': 'string', 'description': 'Reason for switch'}
            },
            'required': ['supplier_id', 'justification']
        },
        'permissions_required': ['modify_suppliers']
    },
    
    'trigger_cost_cutting': {
        'name': 'trigger_cost_cutting',
        'description': 'Initiate cost reduction program',
        'parameters': {
            'type': 'object',
            'properties': {
                'reduction_percent': {
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 0.5,
                    'description': 'Cost reduction percentage'
                },
                'areas': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Areas to cut'
                },
                'justification': {'type': 'string', 'description': 'Reason for cuts'}
            },
            'required': ['reduction_percent', 'areas', 'justification']
        },
        'permissions_required': ['modify_costs']
    },
    
    'pause_expansion': {
        'name': 'pause_expansion',
        'description': 'Pause expansion into a region',
        'parameters': {
            'type': 'object',
            'properties': {
                'region': {'type': 'string', 'description': 'Region to pause'},
                'duration_months': {'type': 'integer', 'minimum': 1, 'description': 'Duration'},
                'justification': {'type': 'string', 'description': 'Reason for pause'}
            },
            'required': ['region', 'duration_months', 'justification']
        },
        'permissions_required': ['modify_expansion']
    }
}

def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """Get tool schema for LLM"""
    return TOOLS.get(tool_name, {})

def get_tools_for_permissions(permissions: list[str]) -> list[Dict[str, Any]]:
    """Get tools available for given permissions"""
    available = []
    for tool_name, tool_def in TOOLS.items():
        required_perms = tool_def.get('permissions_required', [])
        if any(perm in permissions for perm in required_perms):
            available.append(tool_def)
    return available
