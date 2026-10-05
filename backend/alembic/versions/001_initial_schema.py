"""Initial schema with users, sessions, policies, protected_sites, fingerprint_events, masking_events, analytics_events, audit_logs

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. sessions
    op.create_table(
        'sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('client_type', sa.String(length=50), nullable=False, server_default='EXTENSION'),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sessions_token', 'sessions', ['session_token'], unique=True)
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])

    # 3. policies
    op.create_table(
        'policies',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('masking_strength', sa.String(length=50), nullable=False, server_default='BALANCED'),
        sa.Column('protected_signals', sa.JSON(), nullable=False),
        sa.Column('strategy', sa.String(length=50), nullable=False, server_default='DISTRIBUTION_SAMPLED'),
        sa.Column('session_persistence', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('rules_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_policies_user_id', 'policies', ['user_id'])

    # 4. protected_sites
    op.create_table(
        'protected_sites',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('policy_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'domain', name='uq_user_domain')
    )
    op.create_index('ix_protected_sites_domain', 'protected_sites', ['domain'])
    op.create_index('ix_protected_sites_user_id', 'protected_sites', ['user_id'])

    # 5. fingerprint_events
    op.create_table(
        'fingerprint_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('session_id', sa.UUID(), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('signal_type', sa.String(length=50), nullable=False),
        sa.Column('probe_method', sa.String(length=100), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('consistency_score', sa.Float(), nullable=False),
        sa.Column('entropy_estimate', sa.Float(), nullable=False),
        sa.Column('privacy_safe_hash', sa.String(length=64), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_fingerprint_events_domain', 'fingerprint_events', ['domain'])
    op.create_index('ix_fingerprint_events_timestamp', 'fingerprint_events', ['timestamp'])
    op.create_index('ix_fingerprint_events_user_id', 'fingerprint_events', ['user_id'])

    # 6. masking_events
    op.create_table(
        'masking_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('session_id', sa.UUID(), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('signal_type', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('risk_before', sa.Float(), nullable=False),
        sa.Column('risk_after', sa.Float(), nullable=False),
        sa.Column('consistency_before', sa.Float(), nullable=False),
        sa.Column('consistency_after', sa.Float(), nullable=False),
        sa.Column('policy_id', sa.UUID(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_masking_events_domain', 'masking_events', ['domain'])
    op.create_index('ix_masking_events_timestamp', 'masking_events', ['timestamp'])
    op.create_index('ix_masking_events_user_id', 'masking_events', ['user_id'])

    # 7. analytics_events
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='EXTENSION'),
        sa.Column('privacy_safe_metadata', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analytics_events_domain', 'analytics_events', ['domain'])
    op.create_index('ix_analytics_events_timestamp', 'analytics_events', ['timestamp'])
    op.create_index('ix_analytics_events_user_id', 'analytics_events', ['user_id'])

    # 8. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('analytics_events')
    op.drop_table('masking_events')
    op.drop_table('fingerprint_events')
    op.drop_table('protected_sites')
    op.drop_table('policies')
    op.drop_table('sessions')
    op.drop_table('users')
