from typing import Dict, Any, List
from shared.llm import generate_response
import logging
import asyncio

logger = logging.getLogger(__name__)

async def run_agent_turn(
    agent_role: str,
    company_state: Dict[str, Any],
    world_events: List[Dict[str, Any]],
    agent_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a single thinking turn for an agent using LLM.
    """
    
    # Construct Context
    context_str = _build_context_string(company_state, world_events)
    profile_str = _build_profile_string(agent_profile)
    
    system_prompt = f"""You are the {agent_role} of a company.
    
    PROFILE:
    {profile_str}
    
    YOUR GOAL:
    Navigate the current market conditions to maximize your objectives (Profit, Growth, Survival).
    You must balance financial data with human intuition and emotional reaction to news.
    
    OUTPUT FORMAT:
    Return a JSON object with:
    - "thought_process": Internal monologue (1-2 sentences, emotionally colored).
    - "reasoning": Analytical reason for your decision.
    - "emotional_state": Your current feeling (e.g., "Anxious", "Confident", "Greedy").
    - "actions": Key-value pairs of actions (e.g., "hiring": -10, "marketing_spend": 5000).
    """
    
    user_prompt = f"""
    CURRENT SITUATION:
    {context_str}
    
    What is your decision?
    """
    
    response = await generate_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )
    
    return response

def _build_context_string(state: Dict[str, Any], events: List[Dict[str, Any]]) -> str:
    metrics = state.get("metrics", {})
    
    s = f"""
    FINANCIALS:
    - Cash: ${metrics.get('cash', 0):,.2f}
    - Monthly Burn: ${metrics.get('monthly_burn', 0):,.2f}
    - Revenue: ${metrics.get('revenue', 0):,.2f}
    - Runway: {metrics.get('runway_months', 0):.1f} months
    
    RECENT EVENTS:
    """
    
    if not events:
        s += "No major news."
    else:
        for e in events:
            s += f"- [Tick {e.get('tick')}]: {e.get('description')} ({e.get('type')})\n"
            
    return s

def _build_profile_string(profile: Dict[str, Any]) -> str:
    return f"""
    - Risk Appetite: {profile.get('riskAppetite', 0.5)} (0=Safe, 1=Degen)
    - Objectives: {profile.get('objectives', {})}
    - Personality: Analytical but prone to market sentiment.
    """
