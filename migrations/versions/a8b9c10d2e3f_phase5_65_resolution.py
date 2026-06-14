"""phase5_65_resolution

Revision ID: a8b9c10d2e3f
Revises: 094fdf1f7b48
Create Date: 2026-06-13 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8b9c10d2e3f'
down_revision: Union[str, None] = '094fdf1f7b48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. symbol_graph
    op.create_table('symbol_graph',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('symbol_id', sa.String(length=255), nullable=False),
    sa.Column('canonical_name', sa.String(length=255), nullable=False),
    sa.Column('scope_id', sa.String(length=255), nullable=False),
    sa.Column('entity_type', sa.String(length=64), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_symbol_graph_repo', 'symbol_graph', ['repository_id'], unique=False)
    op.create_index('ix_symbol_graph_canonical', 'symbol_graph', ['repository_id', 'canonical_name'], unique=False)

    # 2. symbol_reference
    op.create_table('symbol_reference',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('source_symbol_id', sa.String(length=255), nullable=False),
    sa.Column('target_symbol_id', sa.String(length=255), nullable=False),
    sa.Column('reference_type', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_symbol_ref_repo', 'symbol_reference', ['repository_id'], unique=False)

    # 3. variable_flow
    op.create_table('variable_flow',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=False),
    sa.Column('source_variable', sa.String(length=255), nullable=False),
    sa.Column('target_variable', sa.String(length=255), nullable=False),
    sa.Column('flow_type', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_variable_flow_repo', 'variable_flow', ['repository_id'], unique=False)

    # 4. cross_file_resolution
    op.create_table('cross_file_resolution',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('source_file', sa.Text(), nullable=False),
    sa.Column('source_entity', sa.String(length=255), nullable=False),
    sa.Column('target_file', sa.Text(), nullable=False),
    sa.Column('target_entity', sa.String(length=255), nullable=False),
    sa.Column('relationship_type', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cross_file_res_repo', 'cross_file_resolution', ['repository_id'], unique=False)

    # 5. external_dependency
    op.create_table('external_dependency',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('dependency_name', sa.String(length=255), nullable=False),
    sa.Column('dependency_type', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_external_dep_repo', 'external_dependency', ['repository_id'], unique=False)

    # 6. ai_evidence
    op.create_table('ai_evidence',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=False),
    sa.Column('class_name', sa.String(length=255), nullable=True),
    sa.Column('method_name', sa.String(length=255), nullable=True),
    sa.Column('pattern_matched', sa.String(length=255), nullable=False),
    sa.Column('evidence_type', sa.String(length=64), nullable=False),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_evidence_repo', 'ai_evidence', ['repository_id'], unique=False)

    # 7. repository_architecture_graph
    op.create_table('repository_architecture_graph',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('node_id', sa.String(length=255), nullable=False),
    sa.Column('node_name', sa.String(length=255), nullable=False),
    sa.Column('node_type', sa.String(length=64), nullable=False),
    sa.Column('owner_team', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_repo_arch_repo', 'repository_architecture_graph', ['repository_id'], unique=False)
    op.create_index('ix_repo_arch_node', 'repository_architecture_graph', ['repository_id', 'node_id'], unique=False)

    # 8. architecture_relationship
    op.create_table('architecture_relationship',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('source_node_id', sa.String(length=255), nullable=False),
    sa.Column('target_node_id', sa.String(length=255), nullable=False),
    sa.Column('relationship_type', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_arch_rel_repo', 'architecture_relationship', ['repository_id'], unique=False)

    # 9. repository_structure_graph
    op.create_table('repository_structure_graph',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('source_file_path', sa.Text(), nullable=False),
    sa.Column('target_file_path', sa.Text(), nullable=False),
    sa.Column('relationship_type', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_repo_struct_repo', 'repository_structure_graph', ['repository_id'], unique=False)

    # 10. compiler_output_version
    op.create_table('compiler_output_version',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('file_path', sa.Text(), nullable=False),
    sa.Column('commit_hash', sa.String(length=40), nullable=False),
    sa.Column('compiler_version', sa.String(length=64), nullable=False),
    sa.Column('rules_hash', sa.String(length=64), nullable=False),
    sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comp_out_ver_repo', 'compiler_output_version', ['repository_id'], unique=False)

    # 11. reasoning_artifacts
    op.create_table('reasoning_artifacts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('artifact_type', sa.String(length=64), nullable=False),
    sa.Column('content', sa.JSON(), nullable=False),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('validation_status', sa.String(length=64), nullable=False),
    sa.Column('evidence_refs', sa.JSON(), nullable=False),
    sa.Column('supporting_entities', sa.JSON(), nullable=False),
    sa.Column('supporting_relationships', sa.JSON(), nullable=False),
    sa.Column('supporting_behaviors', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reasoning_art_repo', 'reasoning_artifacts', ['repository_id'], unique=False)

    # 12. knowledge_drifts
    op.create_table('knowledge_drifts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('drift_type', sa.String(length=64), nullable=False),
    sa.Column('element_id', sa.String(length=255), nullable=False),
    sa.Column('from_value', sa.Text(), nullable=False),
    sa.Column('to_value', sa.Text(), nullable=False),
    sa.Column('drift_score', sa.Float(), nullable=False),
    sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_knowledge_drift_repo', 'knowledge_drifts', ['repository_id'], unique=False)

    # 13. external_knowledge_references
    op.create_table('external_knowledge_references',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('source_repository_id', sa.Uuid(), nullable=False),
    sa.Column('target_repository_name', sa.String(length=255), nullable=False),
    sa.Column('dependency_type', sa.String(length=64), nullable=False),
    sa.Column('api_endpoint', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['source_repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ext_know_ref_repo', 'external_knowledge_references', ['source_repository_id'], unique=False)


def downgrade() -> None:
    op.drop_table('external_knowledge_references')
    op.drop_table('knowledge_drifts')
    op.drop_table('reasoning_artifacts')
    op.drop_table('compiler_output_version')
    op.drop_table('repository_structure_graph')
    op.drop_table('architecture_relationship')
    op.drop_table('repository_architecture_graph')
    op.drop_table('ai_evidence')
    op.drop_table('external_dependency')
    op.drop_table('cross_file_resolution')
    op.drop_table('variable_flow')
    op.drop_table('symbol_reference')
    op.drop_table('symbol_graph')
