from datetime import datetime
from typing import List, Dict, Any
import json

class EventLoader:
    """Load and merge event timelines"""
    
    @staticmethod
    def load_pack(pack_name: str) -> List[Dict[str, Any]]:
        """Load event pack from JSON file"""
        import os
        pack_path = os.path.join(
            os.path.dirname(__file__),
            'packs',
            f'{pack_name}.json'
        )
        
        with open(pack_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def merge_events(
        base_events: List[Dict[str, Any]],
        custom_events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge custom events into base timeline"""
        
        all_events = base_events + custom_events
        
        # Sort by timestamp
        all_events.sort(key=lambda e: datetime.fromisoformat(e['timestamp']))
        
        return all_events
    
    @staticmethod
    def validate_timeline(events: List[Dict[str, Any]]) -> bool:
        """Validate timeline consistency"""
        
        for event in events:
            # Required fields
            if not all(k in event for k in ['timestamp', 'event_type', 'severity', 'duration_days']):
                return False
            
            # Severity bounds
            if not 0 <= event['severity'] <= 1:
                return False
            
            # Duration positive
            if event['duration_days'] <= 0:
                return False
            
            # Signals have release times
            for signal in event.get('signals', []):
                if 'release_time' not in signal:
                    return False
        
        return True
    
    @staticmethod
    def stage_signals(event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get staged signals for an event"""
        signals = event.get('signals', [])
        
        # Sort by release time
        signals.sort(key=lambda s: datetime.fromisoformat(s['release_time']))
        
        return signals


class CustomEventBuilder:
    """Builder for creating custom events"""
    
    def __init__(self):
        self.event = {
            'signals': [],
            'affected_areas': [],
            'parameter_impacts': {}
        }
    
    def set_timestamp(self, timestamp: datetime) -> 'CustomEventBuilder':
        self.event['timestamp'] = timestamp.isoformat()
        return self
    
    def set_type(self, event_type: str) -> 'CustomEventBuilder':
        self.event['event_type'] = event_type
        return self
    
    def set_severity(self, severity: float) -> 'CustomEventBuilder':
        if not 0 <= severity <= 1:
            raise ValueError("Severity must be between 0 and 1")
        self.event['severity'] = severity
        return self
    
    def set_duration(self, days: int) -> 'CustomEventBuilder':
        if days <= 0:
            raise ValueError("Duration must be positive")
        self.event['duration_days'] = days
        return self
    
    def add_affected_area(self, area: str) -> 'CustomEventBuilder':
        self.event['affected_areas'].append(area)
        return self
    
    def add_signal(
        self,
        release_time: datetime,
        signal_type: str,
        content: str
    ) -> 'CustomEventBuilder':
        self.event['signals'].append({
            'release_time': release_time.isoformat(),
            'type': signal_type,
            'content': content
        })
        return self
    
    def add_parameter_impact(self, param: str, value: float) -> 'CustomEventBuilder':
        self.event['parameter_impacts'][param] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        # Validate
        required = ['timestamp', 'event_type', 'severity', 'duration_days']
        if not all(k in self.event for k in required):
            raise ValueError(f"Missing required fields: {required}")
        
        return self.event


# Example usage
def create_custom_event_example():
    """Example of creating a custom event"""
    builder = CustomEventBuilder()
    
    event = (builder
        .set_timestamp(datetime(2024, 6, 1))
        .set_type('competitor_launch')
        .set_severity(0.7)
        .set_duration(180)
        .add_affected_area('saas')
        .add_affected_area('tech')
        .add_signal(
            datetime(2024, 5, 15),
            'rumor',
            'Competitor preparing major product launch'
        )
        .add_signal(
            datetime(2024, 6, 1),
            'confirmed',
            'Competitor launches competing product with aggressive pricing'
        )
        .add_parameter_impact('demand_multiplier', 0.85)
        .add_parameter_impact('churn_delta', 0.03)
        .build()
    )
    
    return event
