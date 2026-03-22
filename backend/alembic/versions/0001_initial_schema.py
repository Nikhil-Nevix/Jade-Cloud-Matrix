"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-03-19 09:16:35.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Note: Enums are created automatically by SQLAlchemy when creating tables with Enum columns
    
    # Providers
    op.create_table(
        'providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_providers_id', 'providers', ['id'])
    op.create_index('ix_providers_name', 'providers', ['name'])
    
    # Regions
    op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('region_code', sa.String(100), nullable=False),
        sa.Column('region_name', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_code')
    )
    op.create_index('ix_regions_id', 'regions', ['id'])
    op.create_index('ix_regions_region_code', 'regions', ['region_code'])
    
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', name='user_role'), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Compute Pricing
    op.create_table(
        'compute_pricing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('instance_type', sa.String(100), nullable=False),
        sa.Column('os_type', sa.String(50), nullable=False),
        sa.Column('price_per_hour', sa.Numeric(10, 6), nullable=False),
        sa.Column('price_per_month', sa.Numeric(10, 2), nullable=False),
        sa.Column('price_per_year', sa.Numeric(10, 2), nullable=False),
        sa.Column('vcpu', sa.Integer(), nullable=False),
        sa.Column('memory_gb', sa.Numeric(5, 2), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id', 'region_id', 'instance_type', 'os_type')
    )
    op.create_index('ix_compute_pricing_id', 'compute_pricing', ['id'])
    op.create_index('ix_compute_pricing_instance_type', 'compute_pricing', ['instance_type'])
    op.create_index('ix_compute_pricing_provider_region', 'compute_pricing', ['provider_id', 'region_id'])
    
    # Storage Pricing
    op.create_table(
        'storage_pricing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('storage_type', sa.Enum('block', 'object', name='storage_type'), nullable=False),
        sa.Column('storage_name', sa.String(100), nullable=False),
        sa.Column('price_per_gb', sa.Numeric(10, 6), nullable=False),
        sa.Column('price_per_gb_month', sa.Numeric(10, 6), nullable=False),
        sa.Column('unit_type', sa.String(50), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id', 'region_id', 'storage_type', 'storage_name')
    )
    op.create_index('ix_storage_pricing_id', 'storage_pricing', ['id'])
    op.create_index('ix_storage_pricing_provider_region', 'storage_pricing', ['provider_id', 'region_id'])
    
    # Reserved Pricing
    op.create_table(
        'reserved_pricing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('instance_type', sa.String(100), nullable=False),
        sa.Column('os_type', sa.String(50), nullable=False),
        sa.Column('term', sa.Enum('1yr', '3yr', name='reserved_term'), nullable=False),
        sa.Column('payment_type', sa.Enum('no_upfront', 'partial_upfront', 'all_upfront', name='reserved_type'), nullable=False),
        sa.Column('upfront_cost', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('monthly_cost', sa.Numeric(10, 2), nullable=False),
        sa.Column('effective_hourly', sa.Numeric(10, 6), nullable=False),
        sa.Column('savings_vs_ondemand', sa.Numeric(5, 2), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id', 'region_id', 'instance_type', 'os_type', 'term', 'payment_type')
    )
    op.create_index('ix_reserved_pricing_id', 'reserved_pricing', ['id'])
    op.create_index('ix_reserved_pricing_instance_type', 'reserved_pricing', ['instance_type'])
    op.create_index('ix_reserved_pricing_provider_region', 'reserved_pricing', ['provider_id', 'region_id'])
    
    # Kubernetes Pricing
    op.create_table(
        'kubernetes_pricing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(100), nullable=False),
        sa.Column('vcpu', sa.Integer(), nullable=False),
        sa.Column('memory_gb', sa.Numeric(5, 2), nullable=False),
        sa.Column('price_per_hour', sa.Numeric(10, 6), nullable=False),
        sa.Column('price_per_month', sa.Numeric(10, 2), nullable=False),
        sa.Column('cluster_fee_monthly', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id', 'region_id', 'node_type')
    )
    op.create_index('ix_kubernetes_pricing_id', 'kubernetes_pricing', ['id'])
    op.create_index('ix_kubernetes_pricing_provider_region', 'kubernetes_pricing', ['provider_id', 'region_id'])
    
    # Network Pricing
    op.create_table(
        'network_pricing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('source_region_id', sa.Integer(), nullable=False),
        sa.Column('destination_type', sa.String(100), nullable=False),
        sa.Column('price_per_gb', sa.Numeric(10, 6), nullable=False),
        sa.Column('free_tier_gb', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_region_id'], ['regions.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id', 'source_region_id', 'destination_type')
    )
    op.create_index('ix_network_pricing_id', 'network_pricing', ['id'])
    op.create_index('ix_network_pricing_provider', 'network_pricing', ['provider_id'])
    
    # Calculations
    op.create_table(
        'calculations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('calc_type', sa.String(50), nullable=False, server_default='standard'),
        sa.Column('input_json', sa.JSON(), nullable=False),
        sa.Column('result_json', sa.JSON(), nullable=False),
        sa.Column('cheapest_provider', sa.String(50), nullable=True),
        sa.Column('aws_total_monthly', sa.Numeric(12, 2), nullable=True),
        sa.Column('azure_total_monthly', sa.Numeric(12, 2), nullable=True),
        sa.Column('gcp_total_monthly', sa.Numeric(12, 2), nullable=True),
        sa.Column('duration_months', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calculations_id', 'calculations', ['id'])
    op.create_index('ix_calculations_user_id', 'calculations', ['user_id'])
    op.create_index('ix_calculations_calc_type', 'calculations', ['calc_type'])
    op.create_index('ix_calculations_created_at', 'calculations', ['created_at'], postgresql_using='btree', postgresql_ops={'created_at': 'DESC'})
    
    # Budgets
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('provider', sa.String(50), nullable=True),
        sa.Column('budget_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('period', sa.Enum('monthly', 'quarterly', 'annual', name='budget_period'), nullable=False, server_default='monthly'),
        sa.Column('alert_threshold', sa.Numeric(5, 2), nullable=False, server_default='80.0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_budgets_id', 'budgets', ['id'])
    op.create_index('ix_budgets_user_id', 'budgets', ['user_id'])
    
    # Budget Alerts
    op.create_table(
        'budget_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('budget_id', sa.Integer(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('current_spend', sa.Numeric(12, 2), nullable=False),
        sa.Column('threshold_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('status', sa.Enum('active', 'acknowledged', 'resolved', name='alert_status'), nullable=False, server_default='active'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_budget_alerts_id', 'budget_alerts', ['id'])
    op.create_index('ix_budget_alerts_budget_id', 'budget_alerts', ['budget_id'])
    
    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'], postgresql_using='btree', postgresql_ops={'timestamp': 'DESC'})


def downgrade() -> None:
    op.drop_index('ix_audit_logs_timestamp', 'audit_logs')
    op.drop_index('ix_audit_logs_action', 'audit_logs')
    op.drop_index('ix_audit_logs_user_id', 'audit_logs')
    op.drop_index('ix_audit_logs_id', 'audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index('ix_budget_alerts_budget_id', 'budget_alerts')
    op.drop_index('ix_budget_alerts_id', 'budget_alerts')
    op.drop_table('budget_alerts')
    
    op.drop_index('ix_budgets_user_id', 'budgets')
    op.drop_index('ix_budgets_id', 'budgets')
    op.drop_table('budgets')
    
    op.drop_index('ix_calculations_created_at', 'calculations')
    op.drop_index('ix_calculations_calc_type', 'calculations')
    op.drop_index('ix_calculations_user_id', 'calculations')
    op.drop_index('ix_calculations_id', 'calculations')
    op.drop_table('calculations')
    
    op.drop_index('ix_network_pricing_provider', 'network_pricing')
    op.drop_index('ix_network_pricing_id', 'network_pricing')
    op.drop_table('network_pricing')
    
    op.drop_index('ix_kubernetes_pricing_provider_region', 'kubernetes_pricing')
    op.drop_index('ix_kubernetes_pricing_id', 'kubernetes_pricing')
    op.drop_table('kubernetes_pricing')
    
    op.drop_index('ix_reserved_pricing_provider_region', 'reserved_pricing')
    op.drop_index('ix_reserved_pricing_instance_type', 'reserved_pricing')
    op.drop_index('ix_reserved_pricing_id', 'reserved_pricing')
    op.drop_table('reserved_pricing')
    
    op.drop_index('ix_storage_pricing_provider_region', 'storage_pricing')
    op.drop_index('ix_storage_pricing_id', 'storage_pricing')
    op.drop_table('storage_pricing')
    
    op.drop_index('ix_compute_pricing_provider_region', 'compute_pricing')
    op.drop_index('ix_compute_pricing_instance_type', 'compute_pricing')
    op.drop_index('ix_compute_pricing_id', 'compute_pricing')
    op.drop_table('compute_pricing')
    
    op.drop_index('ix_users_email', 'users')
    op.drop_index('ix_users_id', 'users')
    op.drop_table('users')
    
    op.drop_index('ix_regions_region_code', 'regions')
    op.drop_index('ix_regions_id', 'regions')
    op.drop_table('regions')
    
    op.drop_index('ix_providers_name', 'providers')
    op.drop_index('ix_providers_id', 'providers')
    op.drop_table('providers')
    
    op.execute("DROP TYPE alert_status")
    op.execute("DROP TYPE budget_period")
    op.execute("DROP TYPE reserved_type")
    op.execute("DROP TYPE reserved_term")
    op.execute("DROP TYPE storage_type")
    op.execute("DROP TYPE user_role")
