import pytest
from datetime import datetime, timedelta
from simulation.timelock import TimeLock

def test_future_events_encrypted():
    """Verify future events cannot be accessed"""
    timelock = TimeLock()
    
    current_time = datetime(2020, 1, 1)
    
    events = [
        {
            'timestamp': '2020-01-15T00:00:00Z',
            'event_type': 'future_event',
            'data': 'secret'
        },
        {
            'timestamp': '2019-12-15T00:00:00Z',
            'event_type': 'past_event',
            'data': 'visible'
        }
    ]
    
    encrypted = timelock.encrypt_future_events(events, current_time)
    accessible = timelock.get_accessible_events(encrypted, current_time)
    
    assert len(accessible) == 1
    assert accessible[0]['event_type'] == 'past_event'
    
    future_time = datetime(2020, 2, 1)
    accessible_later = timelock.get_accessible_events(encrypted, future_time)
    
    assert len(accessible_later) == 2

def test_signal_staging():
    """Verify signals are released at correct times"""
    timelock = TimeLock()
    
    event = {
        'timestamp': '2020-03-01T00:00:00Z',
        'event_type': 'staged_event',
        'signals': [
            {
                'release_time': '2020-02-01T00:00:00Z',
                'type': 'rumor',
                'content': 'early signal'
            },
            {
                'release_time': '2020-03-01T00:00:00Z',
                'type': 'confirmed',
                'content': 'confirmed signal'
            }
        ]
    }
    
    encrypted = timelock.encrypt_future_events([event], datetime(2020, 1, 1))
    
    accessible_feb = timelock.get_accessible_events(encrypted, datetime(2020, 2, 15))
    assert len(accessible_feb) == 1
    
    accessible_mar = timelock.get_accessible_events(encrypted, datetime(2020, 3, 15))
    assert len(accessible_mar) == 1
