"""Add instance_equivalence table for multi-cloud instance mapping

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create instance_equivalence table
    op.create_table(
        'instance_equivalence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vcpu_count', sa.Integer(), nullable=False),
        sa.Column('memory_gb', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('aws_instances', JSONB, nullable=False, server_default='[]'),
        sa.Column('azure_instances', JSONB, nullable=False, server_default='[]'),
        sa.Column('gcp_instances', JSONB, nullable=False, server_default='[]'),
        sa.Column('category', sa.String(50), nullable=False, server_default='general_purpose'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_instance_equivalence_id', 'instance_equivalence', ['id'])
    op.create_index('ix_instance_equivalence_vcpu_count', 'instance_equivalence', ['vcpu_count'])
    op.create_index('ix_instance_equivalence_memory_gb', 'instance_equivalence', ['memory_gb'])
    op.create_index('idx_vcpu_memory', 'instance_equivalence', ['vcpu_count', 'memory_gb'])

    # Seed common instance equivalence mappings
    # These are the most common instance configurations across cloud providers
    equivalence_data = [
        # 2 vCPU configurations
        {
            'vcpu': 2, 'memory_gb': 4.0, 'category': 'general_purpose',
            'aws': ['t3.medium', 't3a.medium', 't2.medium'],
            'azure': ['B2s', 'D2s_v3', 'D2as_v4'],
            'gcp': ['e2-medium', 'n1-standard-2', 'n2-standard-2']
        },
        {
            'vcpu': 2, 'memory_gb': 8.0, 'category': 'memory_optimized',
            'aws': ['t3.large', 't3a.large', 'r5.large'],
            'azure': ['D2s_v4', 'E2s_v3'],
            'gcp': ['e2-highmem-2', 'n2-highmem-2']
        },
        # 4 vCPU configurations
        {
            'vcpu': 4, 'memory_gb': 16.0, 'category': 'general_purpose',
            'aws': ['t3.xlarge', 'm5.xlarge', 'm6i.xlarge'],
            'azure': ['D4s_v3', 'D4as_v4', 'B4ms'],
            'gcp': ['n1-standard-4', 'n2-standard-4', 'e2-standard-4']
        },
        {
            'vcpu': 4, 'memory_gb': 32.0, 'category': 'memory_optimized',
            'aws': ['r5.xlarge', 'r6i.xlarge'],
            'azure': ['E4s_v3', 'E4as_v4'],
            'gcp': ['n1-highmem-4', 'n2-highmem-4']
        },
        # 8 vCPU configurations
        {
            'vcpu': 8, 'memory_gb': 32.0, 'category': 'general_purpose',
            'aws': ['t3.2xlarge', 'm5.2xlarge', 'm6i.2xlarge'],
            'azure': ['D8s_v3', 'D8as_v4'],
            'gcp': ['n1-standard-8', 'n2-standard-8', 'e2-standard-8']
        },
        {
            'vcpu': 8, 'memory_gb': 64.0, 'category': 'memory_optimized',
            'aws': ['r5.2xlarge', 'r6i.2xlarge'],
            'azure': ['E8s_v3', 'E8as_v4'],
            'gcp': ['n1-highmem-8', 'n2-highmem-8']
        },
        {
            'vcpu': 8, 'memory_gb': 16.0, 'category': 'compute_optimized',
            'aws': ['c5.2xlarge', 'c6i.2xlarge'],
            'azure': ['F8s_v2'],
            'gcp': ['c2-standard-8', 'n2-highcpu-8']
        },
        # 16 vCPU configurations
        {
            'vcpu': 16, 'memory_gb': 64.0, 'category': 'general_purpose',
            'aws': ['m5.4xlarge', 'm6i.4xlarge'],
            'azure': ['D16s_v3', 'D16as_v4'],
            'gcp': ['n1-standard-16', 'n2-stanard-16']
        },
        {
            'vcpu': 16, 'memory_gb': 128.0, 'category': 'memory_optimized',
            'aws': ['r5.4xlarge', 'r6i.4xlarge'],
            'azure': ['E16s_v3', 'E16as_v4'],
            'gcp': ['n1-highmem-16', 'n2-highmem-16']
        },
        {
            'vcpu': 16, 'memory_gb': 32.0, 'category': 'compute_optimized',
            'aws': ['c5.4xlarge', 'c6i.4xlarge'],
            'azure': ['F16s_v2'],
            'gcp': ['c2-standard-16', 'n2-highcpu-16']
        },
        # 32 vCPU configurations
        {
            'vcpu': 32, 'memory_gb': 128.0, 'category': 'general_purpose',
            'aws': ['m5.8xlarge', 'm6i.8xlarge'],
            'azure': ['D32s_v3', 'D32as_v4'],
            'gcp': ['n1-standard-32', 'n2-standard-32']
        },
        {
            'vcpu': 32, 'memory_gb': 256.0, 'category': 'memory_optimized',
            'aws': ['r5.8xlarge', 'r6i.8xlarge'],
            'azure': ['E32s_v3', 'E32as_v4'],
            'gcp': ['n1-highmem-32', 'n2-highmem-32']
        },
        {
            'vcpu': 32, 'memory_gb': 64.0, 'category': 'compute_optimized',
            'aws': ['c5.8xlarge', 'c6i.8xlarge'],
            'azure': ['F32s_v2'],
            'gcp': ['c2-standard-30', 'n2-highcpu-32']
        },
        # 64 vCPU configurations
        {
            'vcpu': 64, 'memory_gb': 256.0, 'category': 'general_purpose',
            'aws': ['m5.16xlarge', 'm6i.16xlarge'],
            'azure': ['D64s_v3', 'D64as_v4'],
            'gcp': ['n1-standard-64', 'n2-standard-64']
        },
        {
            'vcpu': 64, 'memory_gb': 512.0, 'category': 'memory_optimized',
            'aws': ['r5.16xlarge', 'r6i.16xlarge'],
            'azure': ['E64s_v3', 'E64as_v4'],
            'gcp': ['n1-highmem-64', 'n2-highmem-64']
        },
        {
            'vcpu': 64, 'memory_gb': 128.0, 'category': 'compute_optimized',
            'aws': ['c5.16xlarge', 'c6i.16xlarge'],
            'azure': ['F64s_v2'],
            'gcp': ['c2-standard-60', 'n2-highcpu-64']
        },
        # Additional common configurations
        {
            'vcpu': 1, 'memory_gb': 2.0, 'category': 'general_purpose',
            'aws': ['t3.small', 't3a.small', 't2.small'],
            'azure': ['B1s'],
            'gcp': ['e2-small', 'f1-micro']
        },
        {
            'vcpu': 1, 'memory_gb': 1.0, 'category': 'general_purpose',
            'aws': ['t3.micro', 't3a.micro', 't2.micro'],
            'azure': ['B1ls'],
            'gcp': ['e2-micro', 'f1-micro']
        },
        {
            'vcpu': 96, 'memory_gb': 384.0, 'category': 'general_purpose',
            'aws': ['m5.24xlarge', 'm6i.24xlarge'],
            'azure': ['D96s_v3'],
            'gcp': ['n1-standard-96', 'n2-standard-96']
        },
        {
            'vcpu': 96, 'memory_gb': 768.0, 'category': 'memory_optimized',
            'aws': ['r5.24xlarge', 'r6i.24xlarge'],
            'azure': ['E96s_v3'],
            'gcp': ['n1-highmem-96', 'n2-highmem-96']
        },
    ]

    # Insert equivalence data
    import json
    for data in equivalence_data:
        aws_json = json.dumps(data['aws'])
        azure_json = json.dumps(data['azure'])
        gcp_json = json.dumps(data['gcp'])

        op.execute(f"""
            INSERT INTO instance_equivalence (vcpu_count, memory_gb, aws_instances, azure_instances, gcp_instances, category)
            VALUES ({data['vcpu']}, {data['memory_gb']}, '{aws_json}'::jsonb,
                    '{azure_json}'::jsonb, '{gcp_json}'::jsonb, '{data['category']}')
        """)


def downgrade() -> None:
    op.drop_index('idx_vcpu_memory', table_name='instance_equivalence')
    op.drop_index('ix_instance_equivalence_memory_gb', table_name='instance_equivalence')
    op.drop_index('ix_instance_equivalence_vcpu_count', table_name='instance_equivalence')
    op.drop_index('ix_instance_equivalence_id', table_name='instance_equivalence')
    op.drop_table('instance_equivalence')
