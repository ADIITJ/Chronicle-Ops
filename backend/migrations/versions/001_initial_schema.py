"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_user_tenant', 'users', ['tenant_id'])
    
    # Company Blueprints
    op.create_table(
        'company_blueprints',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('industry', sa.String(), nullable=False),
        sa.Column('initial_conditions', postgresql.JSON(), nullable=False),
        sa.Column('constraints', postgresql.JSON(), nullable=False),
        sa.Column('policies', postgresql.JSON(), nullable=False),
        sa.Column('market_exposure', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'name', 'version', name='uq_blueprint_version')
    )
    op.create_index('idx_blueprint_tenant', 'company_blueprints', ['tenant_id'])
    
    # Event Timelines
    op.create_table(
        'event_timelines',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('events', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'name', 'version', name='uq_timeline_version')
    )
    op.create_index('idx_timeline_tenant', 'event_timelines', ['tenant_id'])
    
    # Agent Configs
    op.create_table(
        'agent_configs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('agents', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'name', 'version', name='uq_agent_config_version')
    )
    op.create_index('idx_agent_config_tenant', 'agent_configs', ['tenant_id'])
    
    # Simulation Runs
    op.create_table(
        'simulation_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('blueprint_id', sa.String(), nullable=False),
        sa.Column('timeline_id', sa.String(), nullable=False),
        sa.Column('agent_config_id', sa.String(), nullable=False),
        sa.Column('seed', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('current_time', sa.DateTime(), nullable=True),
        sa.Column('final_state', postgresql.JSON(), nullable=True),
        sa.Column('metrics', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['agent_config_id'], ['agent_configs.id'], ),
        sa.ForeignKeyConstraint(['blueprint_id'], ['company_blueprints.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['timeline_id'], ['event_timelines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_run_tenant', 'simulation_runs', ['tenant_id'])
    op.create_index('idx_run_status', 'simulation_runs', ['status'])
    
    # Audit Entries
    op.create_table(
        'audit_entries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('sim_time', sa.DateTime(), nullable=False),
        sa.Column('entry_type', sa.String(), nullable=False),
        sa.Column('agent_role', sa.String(), nullable=True),
        sa.Column('action', postgresql.JSON(), nullable=True),
        sa.Column('state_before', postgresql.JSON(), nullable=True),
        sa.Column('state_after', postgresql.JSON(), nullable=True),
        sa.Column('policy_check', postgresql.JSON(), nullable=True),
        sa.Column('signature', sa.Text(), nullable=False),
        sa.Column('prev_signature', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['simulation_runs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_id', 'sequence', name='uq_audit_sequence')
    )
    op.create_index('idx_audit_run', 'audit_entries', ['run_id'])
    op.create_index('idx_audit_sequence', 'audit_entries', ['run_id', 'sequence'])


def downgrade() -> None:
    op.drop_index('idx_audit_sequence', table_name='audit_entries')
    op.drop_index('idx_audit_run', table_name='audit_entries')
    op.drop_table('audit_entries')
    
    op.drop_index('idx_run_status', table_name='simulation_runs')
    op.drop_index('idx_run_tenant', table_name='simulation_runs')
    op.drop_table('simulation_runs')
    
    op.drop_index('idx_agent_config_tenant', table_name='agent_configs')
    op.drop_table('agent_configs')
    
    op.drop_index('idx_timeline_tenant', table_name='event_timelines')
    op.drop_table('event_timelines')
    
    op.drop_index('idx_blueprint_tenant', table_name='company_blueprints')
    op.drop_table('company_blueprints')
    
    op.drop_index('idx_user_tenant', table_name='users')
    op.drop_table('users')
    
    op.drop_table('tenants')
