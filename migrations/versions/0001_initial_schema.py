"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-06-02 21:30:00.000000

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
    # 1. repositories table
    op.create_table(
        'repositories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('default_branch', sa.String(length=100), nullable=False),
        sa.Column('local_path', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )

    # 2. source_files table
    op.create_table(
        'source_files',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=20), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('line_count', sa.Integer(), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_source_files_repo_path', 'source_files', ['repository_id', 'file_path'])

    # 3. code_entities table
    op.create_table(
        'code_entities',
        sa.Column('seid', sa.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(length=30), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('qualified_name', sa.String(length=1000), nullable=False),
        sa.Column('file_id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('parent_seid', sa.UUID(), nullable=True),
        sa.Column('language', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('start_line', sa.Integer(), nullable=False),
        sa.Column('end_line', sa.Integer(), nullable=False),
        sa.Column('start_column', sa.Integer(), nullable=True),
        sa.Column('end_column', sa.Integer(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('structural_fingerprint', sa.String(length=64), nullable=True),
        sa.Column('source_text', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['source_files.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_seid'], ['code_entities.seid'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('seid')
    )
    op.create_index('ix_code_entities_file_id', 'code_entities', ['file_id'])
    op.create_index('ix_code_entities_parent_seid', 'code_entities', ['parent_seid'])
    op.create_index('ix_code_entities_repo_qname', 'code_entities', ['repository_id', 'qualified_name'])
    op.create_index('ix_code_entities_repo_type', 'code_entities', ['repository_id', 'entity_type'])

    # 4. relationships table
    op.create_table(
        'relationships',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('relationship_type', sa.String(length=30), nullable=False),
        sa.Column('source_seid', sa.UUID(), nullable=False),
        sa.Column('target_seid', sa.UUID(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_seid'], ['code_entities.seid'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_seid'], ['code_entities.seid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_seid', 'target_seid', 'relationship_type', name='uq_relationship')
    )
    op.create_index('ix_relationships_repo_type', 'relationships', ['repository_id', 'relationship_type'])
    op.create_index('ix_relationships_source_type', 'relationships', ['source_seid', 'relationship_type'])
    op.create_index('ix_relationships_target_type', 'relationships', ['target_seid', 'relationship_type'])

    # 5. commits table
    op.create_table(
        'commits',
        sa.Column('hash', sa.String(length=40), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('parent_hashes', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('hash')
    )
    op.create_index('ix_commits_repo_id', 'commits', ['repository_id'])
    op.create_index('ix_commits_timestamp', 'commits', ['timestamp'])

    # 6. entity_versions table
    op.create_table(
        'entity_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('seid', sa.UUID(), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('version_ordinal', sa.Integer(), nullable=False),
        sa.Column('mutation_type', sa.String(length=20), nullable=False),
        sa.Column('canonical_name', sa.String(length=1000), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('start_line', sa.Integer(), nullable=False),
        sa.Column('end_line', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('structural_fingerprint', sa.String(length=64), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['commit_hash'], ['commits.hash'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['seid'], ['code_entities.seid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('seid', 'commit_hash', name='ux_entity_versions_seid_commit')
    )
    op.create_index('ix_entity_versions_commit', 'entity_versions', ['commit_hash'])
    op.create_index('ix_entity_versions_seid_ordinal', 'entity_versions', ['seid', 'version_ordinal'])

    # 7. relationship_versions table
    op.create_table(
        'relationship_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('relationship_id', sa.UUID(), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('mutation_type', sa.String(length=20), nullable=False),
        sa.Column('version_ordinal', sa.Integer(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['commit_hash'], ['commits.hash'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['relationship_id'], ['relationships.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_relationship_versions_commit', 'relationship_versions', ['commit_hash'])
    op.create_index('ix_relationship_versions_rel_ordinal', 'relationship_versions', ['relationship_id', 'version_ordinal'])

    # 8. change_events table
    op.create_table(
        'change_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('seid', sa.UUID(), nullable=False),
        sa.Column('change_type', sa.String(length=20), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['commit_hash'], ['commits.hash'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['seid'], ['code_entities.seid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_change_events_commit', 'change_events', ['commit_hash'])
    op.create_index('ix_change_events_repo', 'change_events', ['repository_id'])
    op.create_index('ix_change_events_seid', 'change_events', ['seid'])

    # 9. repository_snapshots table
    op.create_table(
        'repository_snapshots',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('entity_seids', sa.JSON(), nullable=False),
        sa.Column('snapshot_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['commit_hash'], ['commits.hash'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repository_id', 'commit_hash', name='ux_snapshots_repo_commit')
    )

def downgrade() -> None:
    op.drop_table('repository_snapshots')
    op.drop_index('ix_change_events_seid', table_name='change_events')
    op.drop_index('ix_change_events_repo', table_name='change_events')
    op.drop_index('ix_change_events_commit', table_name='change_events')
    op.drop_table('change_events')
    op.drop_index('ix_relationship_versions_rel_ordinal', table_name='relationship_versions')
    op.drop_index('ix_relationship_versions_commit', table_name='relationship_versions')
    op.drop_table('relationship_versions')
    op.drop_index('ix_entity_versions_seid_ordinal', table_name='entity_versions')
    op.drop_index('ix_entity_versions_commit', table_name='entity_versions')
    op.drop_table('entity_versions')
    op.drop_index('ix_commits_timestamp', table_name='commits')
    op.drop_index('ix_commits_repo_id', table_name='commits')
    op.drop_table('commits')
    op.drop_index('ix_relationships_target_type', table_name='relationships')
    op.drop_index('ix_relationships_source_type', table_name='relationships')
    op.drop_index('ix_relationships_repo_type', table_name='relationships')
    op.drop_table('relationships')
    op.drop_index('ix_code_entities_repo_type', table_name='code_entities')
    op.drop_index('ix_code_entities_repo_qname', table_name='code_entities')
    op.drop_index('ix_code_entities_parent_seid', table_name='code_entities')
    op.drop_index('ix_code_entities_file_id', table_name='code_entities')
    op.drop_table('code_entities')
    op.drop_index('ix_source_files_repo_path', table_name='source_files')
    op.drop_table('source_files')
    op.drop_table('repositories')
