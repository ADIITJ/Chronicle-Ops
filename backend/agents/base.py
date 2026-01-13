from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from ..simulation.timelock import InformationContext
from ..simulation.state import CompanyState
import uuid
import os
import httpx

class Tool:
    """Agent tool definition"""
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert to LLM tool schema"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters
        }

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(
        self,
        role: str,
        objectives: Dict[str, float],
        permissions: List[str],
        approval_threshold: float,
        risk_appetite: float
    ):
        self.role = role
        self.objectives = objectives
        self.permissions = permissions
        self.approval_threshold = approval_threshold
        self.risk_appetite = risk_appetite
        self.tools = self._register_tools()
        self.api_key = os.getenv("OPENROUTER_API_KEY", "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")
        self.model = "mistralai/mistral-small-2409:free"
    
    @abstractmethod
    def _register_tools(self) -> List[Tool]:
        """Register tools available to this agent"""
        pass
    
    def can_execute(self, action_type: str) -> bool:
        """Check if agent has permission for action"""
        return action_type in self.permissions
    
    def needs_approval(self, action: Dict[str, Any]) -> bool:
        """Check if action requires approval"""
        estimated_impact = action.get('estimated_impact', 0)
        return estimated_impact > self.approval_threshold
    
    async def decide(
        self,
        context: InformationContext,
        state: CompanyState,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Make decision based on context and state"""
        
        prompt = self._build_prompt(context, state, constraints)
        tool_schemas = [tool.to_schema() for tool in self.tools]
        
        actions = await self._call_llm(prompt, tool_schemas)
        
        for action in actions:
            action['id'] = str(uuid.uuid4())
            action['agent_role'] = self.role
            action['timestamp'] = datetime.utcnow().isoformat()
        
        return actions
    
    def _build_prompt(
        self,
        context: InformationContext,
        state: CompanyState,
        constraints: Dict[str, Any]
    ) -> str:
        """Build decision prompt"""
        return f"""You are the {self.role} of a company.

Current State:
- Cash: ${state.cash:,.2f}
- Runway: {state.runway_months:.1f} months
- Revenue (monthly): ${state.revenue_monthly:,.2f}
- Costs (monthly): ${state.costs_monthly:,.2f}
- Headcount: {state.headcount}
- Service Level: {state.service_level:.2%}

Your Objectives:
{self._format_objectives()}

Observable Events:
{self._format_events(context)}

Constraints:
{self._format_constraints(constraints)}

Based on this information, what actions should you take? Use the available tools to propose actions.
Consider your risk appetite ({self.risk_appetite}) when making decisions.
Only propose actions you have permission to execute.
"""
    
    def _format_objectives(self) -> str:
        return '\n'.join([f"- {obj}: {weight}" for obj, weight in self.objectives.items()])
    
    def _format_events(self, context: InformationContext) -> str:
        events = context.get_observable_events()
        if not events:
            return "No recent events"
        return '\n'.join([f"- {e.get('event_type')}: {e.get('severity')}" for e in events[:5]])
    
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        return '\n'.join([f"- {k}: {v}" for k, v in constraints.items()])
    
    async def _call_llm(self, prompt: str, tool_schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Call Mistral AI via OpenRouter"""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"You are a {self.role} agent making business decisions. Respond with JSON array of actions using available tools."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000,
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Parse JSON response
                    import json
                    try:
                        actions = json.loads(content)
                        if isinstance(actions, dict):
                            actions = [actions]
                        return actions
                    except json.JSONDecodeError:
                        # If not valid JSON, extract actions from text
                        return self._extract_actions_from_text(content)
                else:
                    print(f"LLM API error: {response.status_code}")
                    return []
                    
            except Exception as e:
                print(f"LLM call failed: {e}")
                return []
    
    def _extract_actions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract actions from LLM text response"""
        # Simple heuristic: look for action keywords
        actions = []
        
        if "no action" in text.lower() or "maintain" in text.lower():
            return []
        
        # Conservative default: no action if can't parse
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent config"""
        return {
            'role': self.role,
            'objectives': self.objectives,
            'permissions': self.permissions,
            'approval_threshold': self.approval_threshold,
            'risk_appetite': self.risk_appetite,
            'tools': [tool.name for tool in self.tools]
        }
