import pytest
from datetime import datetime
from audit.ledger import AuditLedger
import threading
import time

def test_audit_chain_integrity():
    """Verify audit chain cannot be tampered"""
    ledger = AuditLedger()
    
    for i in range(10):
        ledger.append(
            run_id='test-run',
            sim_time=datetime.utcnow(),
            entry_type='test',
            data={'value': i}
        )
    
    assert ledger.verify_chain('test-run')
    
    entries = ledger.get_entries('test-run')
    entries[5]['data']['value'] = 999
    
    assert not ledger.verify_chain('test-run')

def test_concurrent_writes():
    """Verify concurrent writes maintain integrity"""
    ledger = AuditLedger()
    errors = []
    
    def write_entries(run_id, count):
        try:
            for i in range(count):
                ledger.append(
                    run_id=run_id,
                    sim_time=datetime.utcnow(),
                    entry_type='concurrent_test',
                    data={'thread': run_id, 'index': i}
                )
        except Exception as e:
            errors.append(e)
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=write_entries, args=(f'run-{i}', 20))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    assert len(errors) == 0
    
    for i in range(5):
        assert ledger.verify_chain(f'run-{i}')
        entries = ledger.get_entries(f'run-{i}')
        assert len(entries) == 20

def test_entry_idempotency():
    """Verify duplicate entries are handled"""
    ledger = AuditLedger()
    
    entry_id = 'unique-entry-1'
    
    sig1 = ledger.append(
        run_id='test-run',
        sim_time=datetime.utcnow(),
        entry_type='test',
        data={'value': 1},
        entry_id=entry_id
    )
    
    sig2 = ledger.append(
        run_id='test-run',
        sim_time=datetime.utcnow(),
        entry_type='test',
        data={'value': 2},
        entry_id=entry_id
    )
    
    assert sig1 == sig2
    
    entries = ledger.get_entries('test-run')
    assert len(entries) == 1

def test_bundle_export_verification():
    """Verify exported bundles can be verified"""
    ledger = AuditLedger()
    
    for i in range(5):
        ledger.append(
            run_id='export-test',
            sim_time=datetime.utcnow(),
            entry_type='test',
            data={'value': i}
        )
    
    bundle = ledger.export_bundle('export-test')
    
    assert 'bundle_signature' in bundle
    assert 'bundle_hash' in bundle
    assert bundle['entry_count'] == 5
    assert len(bundle['entries']) == 5
