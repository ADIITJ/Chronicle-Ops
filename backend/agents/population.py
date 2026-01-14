from typing import Dict, Any, List
from .base import BaseAgent

class PopulationAgent(BaseAgent):
    """
    Population/Market Agent - Models consumer behavior, market sentiment, and public opinion
    
    This agent represents the aggregate behavior of the market/population and influences:
    - Product popularity and viral growth
    - Sales conversion rates
    - Brand perception and reputation
    - Market sentiment and trends
    - Word-of-mouth effects
    - Social media influence
    """
    
    def __init__(
        self,
        objectives: Dict[str, float] = None,
        permissions: List[str] = None,
        approval_threshold: float = 0,
        risk_appetite: float = 0.5
    ):
        default_objectives = {
            'product_satisfaction': 0.3,
            'value_perception': 0.25,
            'brand_trust': 0.25,
            'market_fit': 0.2
        }
        
        default_permissions = [
            'influence_demand',
            'affect_conversion',
            'impact_reputation',
            'drive_virality'
        ]
        
        super().__init__(
            role='population',
            objectives=objectives or default_objectives,
            permissions=permissions or default_permissions,
            approval_threshold=approval_threshold,
            risk_appetite=risk_appetite
        )
        
        # Population-specific state
        self.sentiment_score = 0.5  # 0-1 scale
        self.awareness_level = 0.1  # 0-1 scale
        self.trust_level = 0.5  # 0-1 scale
        self.viral_coefficient = 1.0  # Multiplier for organic growth
    
    def evaluate_state(self, state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate current market conditions and population sentiment
        
        Returns market dynamics that affect company performance
        """
        
        # Extract relevant metrics
        pricing = state.get('pricing', {})
        service_level = state.get('service_level', 0.95)
        growth_rate = state.get('growth_rate', 0.1)
        churn_rate = state.get('churn_rate', 0.05)
        market_share = state.get('market_share', 0.05)
        
        # Evaluate pricing perception
        avg_price = sum(pricing.values()) / len(pricing) if pricing else 100
        price_perception = self._evaluate_price_perception(avg_price, state)
        
        # Evaluate product quality perception
        quality_perception = self._evaluate_quality(service_level, churn_rate)
        
        # Evaluate brand strength
        brand_strength = self._evaluate_brand(market_share, growth_rate)
        
        # Calculate overall sentiment
        self.sentiment_score = (
            price_perception * 0.3 +
            quality_perception * 0.4 +
            brand_strength * 0.3
        )
        
        # Update awareness based on marketing and growth
        marketing_spend = state.get('marketing_budget', 0)
        self.awareness_level = min(1.0, self.awareness_level + (marketing_spend / 1000000) * 0.1 + growth_rate * 0.05)
        
        # Update trust based on service quality and consistency
        self.trust_level = 0.7 * self.trust_level + 0.3 * quality_perception
        
        # Calculate viral coefficient
        self.viral_coefficient = 1.0 + (self.sentiment_score - 0.5) * 2.0  # Range: 0.0 to 2.0
        
        return {
            'sentiment_score': self.sentiment_score,
            'awareness_level': self.awareness_level,
            'trust_level': self.trust_level,
            'viral_coefficient': self.viral_coefficient,
            'price_perception': price_perception,
            'quality_perception': quality_perception,
            'brand_strength': brand_strength,
            'market_dynamics': self._generate_market_dynamics()
        }
    
    def _evaluate_price_perception(self, price: float, state: Dict[str, Any]) -> float:
        """Evaluate how population perceives pricing"""
        # Compare to market average (assumed baseline)
        market_avg = 100
        price_ratio = price / market_avg
        
        # Optimal price is around market average
        if price_ratio < 0.7:
            return 0.6  # Too cheap, perceived as low quality
        elif price_ratio < 0.9:
            return 0.9  # Good value
        elif price_ratio < 1.1:
            return 0.8  # Fair price
        elif price_ratio < 1.3:
            return 0.6  # Expensive but acceptable
        else:
            return 0.3  # Too expensive
    
    def _evaluate_quality(self, service_level: float, churn_rate: float) -> float:
        """Evaluate perceived product/service quality"""
        # High service level and low churn = high quality perception
        quality_score = service_level * 0.7 + (1 - min(churn_rate * 10, 1.0)) * 0.3
        return max(0, min(1, quality_score))
    
    def _evaluate_brand(self, market_share: float, growth_rate: float) -> float:
        """Evaluate brand strength and market position"""
        # Larger market share and positive growth = stronger brand
        brand_score = (market_share * 10) * 0.6 + min(growth_rate * 5, 1.0) * 0.4
        return max(0, min(1, brand_score))
    
    def _generate_market_dynamics(self) -> Dict[str, float]:
        """Generate market dynamics that affect company performance"""
        return {
            'demand_multiplier': 0.5 + self.sentiment_score * 1.0,  # Range: 0.5 to 1.5
            'conversion_rate_modifier': self.trust_level,  # Range: 0 to 1
            'organic_growth_boost': (self.viral_coefficient - 1.0) * 0.1,  # Range: -0.1 to 0.1
            'churn_impact': (1 - self.sentiment_score) * 0.05,  # Range: 0 to 0.05
            'word_of_mouth_factor': self.viral_coefficient,
            'brand_equity': self.trust_level * self.awareness_level
        }
    
    async def decide(self, state: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Population agent doesn't take direct actions but influences market dynamics
        
        Returns market influence effects rather than company actions
        """
        
        evaluation = self.evaluate_state(state, context)
        
        # Generate market influence "actions" that affect company performance
        influences = []
        
        # Influence demand based on sentiment
        if self.sentiment_score > 0.7:
            influences.append({
                'type': 'market_influence',
                'effect': 'demand_surge',
                'magnitude': (self.sentiment_score - 0.7) * 2,
                'reason': f'High market sentiment ({self.sentiment_score:.2f}) driving increased demand'
            })
        elif self.sentiment_score < 0.3:
            influences.append({
                'type': 'market_influence',
                'effect': 'demand_decline',
                'magnitude': (0.3 - self.sentiment_score) * 2,
                'reason': f'Low market sentiment ({self.sentiment_score:.2f}) reducing demand'
            })
        
        # Viral growth effects
        if self.viral_coefficient > 1.3:
            influences.append({
                'type': 'market_influence',
                'effect': 'viral_growth',
                'magnitude': self.viral_coefficient - 1.0,
                'reason': f'Strong word-of-mouth (coefficient: {self.viral_coefficient:.2f}) driving viral growth'
            })
        
        # Brand reputation effects
        if self.trust_level > 0.8 and self.awareness_level > 0.5:
            influences.append({
                'type': 'market_influence',
                'effect': 'brand_premium',
                'magnitude': self.trust_level * self.awareness_level,
                'reason': f'Strong brand (trust: {self.trust_level:.2f}, awareness: {self.awareness_level:.2f}) enabling premium positioning'
            })
        
        return influences
