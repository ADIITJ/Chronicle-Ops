import pytest
from shared.auth import AuthContext

def test_tenant_isolation():
    """Verify tenants cannot access each other's data"""
    tenant1 = AuthContext(
        user_id='user1',
        tenant_id='tenant1',
        role='admin'
    )
    
    tenant2 = AuthContext(
        user_id='user2',
        tenant_id='tenant2',
        role='admin'
    )
    
    assert tenant1.can_read('tenant1')
    assert not tenant1.can_read('tenant2')
    
    assert tenant2.can_read('tenant2')
    assert not tenant2.can_read('tenant1')

def test_role_permissions():
    """Verify role-based permissions"""
    admin = AuthContext(
        user_id='admin',
        tenant_id='tenant1',
        role='admin'
    )
    
    viewer = AuthContext(
        user_id='viewer',
        tenant_id='tenant1',
        role='viewer'
    )
    
    assert admin.can_write('tenant1')
    assert not viewer.can_write('tenant1')
    
    assert viewer.can_read('tenant1')
