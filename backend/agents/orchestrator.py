from typing import Dict, Any, List, Optional
from datetime import datetime
from ..agents.base import BaseAgent
from ..simulation.engine import SimulationEngine
from ..policy.engine import PolicyEngine, PolicyDecision
import asyncio

class AgentOrchestrator:
    """Orchestrates multi-agent decision making"""
    
    def __init__(
        self,
        agents: List[BaseAgent],
        policy_engine: PolicyEngine,
        simulation: SimulationEngine
    ):
        self.agents = {agent.role: agent for agent in agents}
        self.policy_engine = policy_engine
        self.simulation = simulation
        self.pending_approvals: List[Dict[str, Any]] = []
    
    async def run_decision_cycle(self) -> List[Dict[str, Any]]:
        """Run one decision cycle for all agents"""
        
        context = self.simulation.get_information_context()
        state = self.simulation.state
        constraints = self.simulation.blueprint.get('constraints', {})
        
        all_actions = []
        market_dynamics = {}
        
        # STEP 1: Run Population agent FIRST to establish market conditions
        if 'population' in self.agents:
            population_agent = self.agents['population']
            market_evaluation = population_agent.evaluate_state(state.to_dict(), context)
            market_dynamics = market_evaluation.get('market_dynamics', {})
            
            # Store market state in database
            await self._store_market_state(market_evaluation)
            
            # Get market influence actions
            population_influences = await population_agent.decide(state.to_dict(), context)
            all_actions.extend(population_influences)
        
        # STEP 2: Run other agents with market context
        tasks = []
        enhanced_context = {
            **context,
            'market_dynamics': market_dynamics,
            'market_sentiment': market_dynamics.get('demand_multiplier', 1.0)
        }
        
        for role, agent in self.agents.items():
            if role != 'population':  # Skip population, already ran
                tasks.append(self._get_agent_decision(agent, enhanced_context, state, constraints))
        
        agent_decisions = await asyncio.gather(*tasks)
        
        # Flatten and process
        for decisions in agent_decisions:
            for action in decisions:
                all_actions.append(action)
        
        # Evaluate and execute actions
        results = []
        for action in all_actions:
            result = await self._evaluate_and_execute(action)
            results.append(result)
        
        return results
    
    async def _get_agent_decision(self, agent: BaseAgent, context: Dict[str, Any], state: Any, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get decision from a single agent with full context"""
        decisions = await agent.decide(context, state.to_dict(), constraints)
        
        # Store agent decision in database
        for decision in decisions:
            await self._store_agent_decision(agent.role, context, decision)
        
        return decisions
    
    async def _store_market_state(self, market_evaluation: Dict[str, Any]):
        """Store market state to database"""
        # TODO: Implement database storage
        pass
    
    async def _store_agent_decision(self, agent_role: str, observations: Dict[str, Any], decision: Dict[str, Any]):
        """Store agent decision to database"""
        # TODO: Implement database storage
        pass
    
    async def _evaluate_and_execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate action through policy engine and execute if approved"""
        
        agent_role = action.get('agent_role')
        
        # Check permissions
        agent = self.agents.get(agent_role)
        if not agent or not agent.can_execute(action['type']):
            return {
                'action': action,
                'status': 'denied',
                'reason': 'Insufficient permissions'
            }
        
        # Policy check
        policy_result = self.policy_engine.evaluate_action(
            action,
            self.simulation.state.to_dict(),
            agent_role
        )
        
        if policy_result.decision == PolicyDecision.DENY:
            return {
                'action': action,
                'status': 'denied',
                'reason': policy_result.reason,
                'violated_rules': policy_result.violated_rules
            }
        
        if policy_result.decision == PolicyDecision.ESCALATE:
            # Add to pending approvals
            self.pending_approvals.append({
                'action': action,
                'reason': policy_result.reason,
                'timestamp': datetime.utcnow().isoformat()
            })
            return {
                'action': action,
                'status': 'pending_approval',
                'reason': policy_result.reason
            }
        
        # Execute action
        success = self.simulation.apply_action(action, agent_role)
        
        if success:
            return {
                'action': action,
                'status': 'executed',
                'reason': 'Action applied successfully'
            }
        else:
            return {
                'action': action,
                'status': 'failed',
                'reason': 'Action failed validation'
            }
    
    def approve_action(self, action_id: str, approved_by: str) -> bool:
        """Approve a pending action"""
        for i, pending in enumerate(self.pending_approvals):
            if pending['action'].get('id') == action_id:
                action = pending['action']
                success = self.simulation.apply_action(action, action['agent_role'])
                if success:
                    self.pending_approvals.pop(i)
                return success
        return False
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approvals"""
        return self.pending_approvals.copy()
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of all agents"""
        return {
            role: agent.to_dict()
            for role, agent in self.agents.items()
        }
