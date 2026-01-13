import pytest
from datetime import datetime
from simulation.engine import SimulationEngine
import copy

def test_same_seed_same_outcome():
    """Verify deterministic execution"""
    blueprint = {
        'industry': 'saas',
        'initial_conditions': {
            'cash': 5000000,
            'monthlyBurn': 200000,
            'headcount': 20
        },
        'constraints': {},
        'policies': {}
    }
    
    timeline = {
        'start_date': '2020-01-01T00:00:00Z',
        'end_date': '2020-12-31T00:00:00Z',
        'events': []
    }
    
    seed = 42
    
    sim1 = SimulationEngine(blueprint, timeline, seed)
    sim2 = SimulationEngine(blueprint, timeline, seed)
    
    for _ in range(10):
        sim1.tick()
        sim2.tick()
    
    assert sim1.state.cash == sim2.state.cash
    assert sim1.state.headcount == sim2.state.headcount
    assert sim1.state.hash() == sim2.state.hash()

def test_checkpoint_restore_determinism():
    """Verify checkpoint/restore maintains determinism"""
    blueprint = {
        'industry': 'saas',
        'initial_conditions': {
            'cash': 5000000,
            'monthlyBurn': 200000,
            'headcount': 20
        },
        'constraints': {},
        'policies': {}
    }
    
    timeline = {
        'start_date': '2020-01-01T00:00:00Z',
        'end_date': '2020-12-31T00:00:00Z',
        'events': []
    }
    
    sim1 = SimulationEngine(blueprint, timeline, 42)
    
    for _ in range(5):
        sim1.tick()
    
    checkpoint = sim1.checkpoint()
    
    for _ in range(5):
        sim1.tick()
    
    final_state1 = sim1.state.hash()
    
    sim2 = SimulationEngine(blueprint, timeline, 42, recovery_checkpoint=checkpoint)
    
    for _ in range(5):
        sim2.tick()
    
    final_state2 = sim2.state.hash()
    
    assert final_state1 == final_state2

def test_action_idempotency():
    """Verify actions are idempotent"""
    blueprint = {
        'industry': 'saas',
        'initial_conditions': {
            'cash': 5000000,
            'monthlyBurn': 200000,
            'headcount': 20
        },
        'constraints': {},
        'policies': {}
    }
    
    timeline = {
        'start_date': '2020-01-01T00:00:00Z',
        'end_date': '2020-12-31T00:00:00Z',
        'events': []
    }
    
    sim = SimulationEngine(blueprint, timeline, 42)
    
    action = {
        'id': 'test-action-1',
        'type': 'adjust_hiring',
        'params': {'delta': 5}
    }
    
    initial_headcount = sim.state.headcount
    
    sim.apply_action(action)
    headcount_after_first = sim.state.headcount
    
    sim.apply_action(action)
    headcount_after_second = sim.state.headcount
    
    assert headcount_after_first == initial_headcount + 5
    assert headcount_after_second == headcount_after_first

def test_crash_recovery():
    """Verify crash recovery works"""
    blueprint = {
        'industry': 'saas',
        'initial_conditions': {
            'cash': 5000000,
            'monthlyBurn': 200000,
            'headcount': 20
        },
        'constraints': {},
        'policies': {}
    }
    
    timeline = {
        'start_date': '2020-01-01T00:00:00Z',
        'end_date': '2020-12-31T00:00:00Z',
        'events': []
    }
    
    sim1 = SimulationEngine(blueprint, timeline, 42)
    
    for _ in range(5):
        sim1.tick()
    
    checkpoint = sim1.checkpoint()
    
    sim2 = SimulationEngine(blueprint, timeline, 42, recovery_checkpoint=checkpoint)
    
    assert sim2.state.hash() == sim1.state.hash()
    assert sim2.current_time == sim1.current_time

def test_checkpoint_corruption_detection():
    """Verify corrupted checkpoints are rejected"""
    blueprint = {
        'industry': 'saas',
        'initial_conditions': {
            'cash': 5000000,
            'monthlyBurn': 200000,
            'headcount': 20
        },
        'constraints': {},
        'policies': {}
    }
    
    timeline = {
        'start_date': '2020-01-01T00:00:00Z',
        'end_date': '2020-12-31T00:00:00Z',
        'events': []
    }
    
    sim = SimulationEngine(blueprint, timeline, 42)
    sim.tick()
    
    checkpoint = sim.checkpoint()
    checkpoint['state']['cash'] = 9999999
    
    with pytest.raises(ValueError, match="corrupted"):
        SimulationEngine(blueprint, timeline, 42, recovery_checkpoint=checkpoint)
