from datetime import datetime
from typing import List, Dict, Any, Optional
from cryptography.fernet import Fernet
import json
import os

class TimeLock:
    """Enforces time-lock constraints: agents cannot access future information"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_future_events(self, events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Encrypt events that occur after current_time"""
        result = []
        for event in events:
            event_time = datetime.fromisoformat(event['timestamp']) if isinstance(event['timestamp'], str) else event['timestamp']
            
            if event_time > current_time:
                # Encrypt future event
                encrypted_data = self.cipher.encrypt(json.dumps(event).encode())
                result.append({
                    'timestamp': event['timestamp'],
                    'encrypted': True,
                    'data': encrypted_data.decode()
                })
            else:
                # Past/present event remains accessible
                result.append({**event, 'encrypted': False})
        
        return result
    
    def get_accessible_events(self, events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Return only events up to current_time"""
        accessible = []
        for event in events:
            if event.get('encrypted'):
                continue
            
            event_time = datetime.fromisoformat(event['timestamp']) if isinstance(event['timestamp'], str) else event['timestamp']
            if event_time <= current_time:
                accessible.append(event)
        
        return accessible
    
    def get_accessible_signals(self, event: Dict[str, Any], current_time: datetime) -> List[Dict[str, Any]]:
        """Return only signals that have been released by current_time"""
        signals = event.get('signals', [])
        accessible = []
        
        for signal in signals:
            release_time = datetime.fromisoformat(signal['release_time']) if isinstance(signal['release_time'], str) else signal['release_time']
            if release_time <= current_time:
                accessible.append(signal)
        
        return accessible

class InformationContext:
    """Provides time-locked view of world state for agents"""
    
    def __init__(self, current_time: datetime, timelock: TimeLock, events: List[Dict[str, Any]]):
        self.current_time = current_time
        self.timelock = timelock
        self.all_events = events
    
    def get_observable_events(self) -> List[Dict[str, Any]]:
        """Get events observable at current_time"""
        return self.timelock.get_accessible_events(self.all_events, self.current_time)
    
    def get_event_signals(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get signals for an event that have been released"""
        return self.timelock.get_accessible_signals(event, self.current_time)
    
    def can_access_data(self, data_timestamp: datetime) -> bool:
        """Check if data from data_timestamp is accessible"""
        return data_timestamp <= self.current_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize context for agent consumption"""
        return {
            'current_time': self.current_time.isoformat(),
            'observable_events': self.get_observable_events(),
            'access_note': 'Only information up to current_time is accessible'
        }

def verify_no_future_access(agent_input: Dict[str, Any], current_time: datetime) -> bool:
    """Verify agent input doesn't contain future information"""
    
    # Check if any timestamps in input are beyond current_time
    def check_timestamps(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['timestamp', 'time', 'date'] and isinstance(value, (str, datetime)):
                    ts = datetime.fromisoformat(value) if isinstance(value, str) else value
                    if ts > current_time:
                        raise ValueError(f"Future timestamp detected at {path}.{key}: {ts} > {current_time}")
                check_timestamps(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_timestamps(item, f"{path}[{i}]")
    
    try:
        check_timestamps(agent_input)
        return True
    except ValueError:
        return False
