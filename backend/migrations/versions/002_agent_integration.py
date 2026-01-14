"""Add agent decisions and market state tables

Revision ID: 002_agent_integration
Revises: 001_initial
Create Date: 2026-01-14 23:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_agent_integration'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agent decisions table - stores full reasoning chains
    op.create_table(
        'agent_decisions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('tick', sa.Integer(), nullable=False),
        sa.Column('agent_role', sa.String(50), nullable=False),
        sa.Column('observations', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('proposed_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=False, default=False),
        sa.Column('executed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['run_id'], ['simulation_runs.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_agent_decisions_run', 'agent_decisions', ['run_id'])
    op.create_index('idx_agent_decisions_tick', 'agent_decisions', ['run_id', 'tick'])
    op.create_index('idx_agent_decisions_role', 'agent_decisions', ['agent_role'])

    # Market state table - tracks population metrics over time
    op.create_table(
        'market_state',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('tick', sa.Integer(), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('awareness_level', sa.Float(), nullable=False),
        sa.Column('trust_level', sa.Float(), nullable=False),
        sa.Column('viral_coefficient', sa.Float(), nullable=False),
        sa.Column('market_dynamics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('price_perception', sa.Float(), nullable=True),
        sa.Column('quality_perception', sa.Float(), nullable=True),
        sa.Column('brand_strength', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['run_id'], ['simulation_runs.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_market_state_run', 'market_state', ['run_id'])
    op.create_index('idx_market_state_tick', 'market_state', ['run_id', 'tick'])

    # Event responses table - logs how agents react to events
    op.create_table(
        'event_responses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('event_id', sa.String(), nullable=True),
        sa.Column('tick', sa.Integer(), nullable=False),
        sa.Column('agent_role', sa.String(50), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_description', sa.Text(), nullable=False),
        sa.Column('agent_response', sa.Text(), nullable=True),
        sa.Column('actions_taken', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['run_id'], ['simulation_runs.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_event_responses_run', 'event_responses', ['run_id'])
    op.create_index('idx_event_responses_tick', 'event_responses', ['run_id', 'tick'])
    op.create_index('idx_event_responses_event', 'event_responses', ['event_id'])
    op.create_index('idx_event_responses_agent', 'event_responses', ['agent_role'])


def downgrade() -> None:
    op.drop_index('idx_event_responses_agent', table_name='event_responses')
    op.drop_index('idx_event_responses_event', table_name='event_responses')
    op.drop_index('idx_event_responses_tick', table_name='event_responses')
    op.drop_index('idx_event_responses_run', table_name='event_responses')
    op.drop_table('event_responses')
    
    op.drop_index('idx_market_state_tick', table_name='market_state')
    op.drop_index('idx_market_state_run', table_name='market_state')
    op.drop_table('market_state')
    
    op.drop_index('idx_agent_decisions_role', table_name='agent_decisions')
    op.drop_index('idx_agent_decisions_tick', table_name='agent_decisions')
    op.drop_index('idx_agent_decisions_run', table_name='agent_decisions')
    op.drop_table('agent_decisions')
