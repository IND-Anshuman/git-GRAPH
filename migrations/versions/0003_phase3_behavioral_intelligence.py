"""phase3_behavioral_intelligence

Revision ID: 0003_phase3
Revises: b357ef00886f
Create Date: 2026-06-05 20:08:31.000000

Adds 11 tables for Phase 3 Behavioral Intelligence:
  - ontology_nodes          : hierarchical taxonomy nodes for code pattern categories
  - behavior_patterns       : canonical pattern definitions referencing ontology nodes
  - logic_signatures        : per-repository behavioral fingerprints for a code entity
  - logic_versions          : point-in-time snapshots of a logic signature at a commit
  - logic_evidence          : raw AST / textual evidence supporting a logic version
  - logic_transitions       : detected behavioral changes between two logic versions
  - behavior_explanations   : human-readable narrative for a logic version
  - behavior_drift          : aggregate drift metrics linking transitions to versions
  - logic_clusters          : groupings of similar logic signatures across repositories
  - logic_cluster_members   : membership table linking signatures to clusters
  - logic_version_patterns  : many-to-many join of logic versions to behavior patterns
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_phase3'
down_revision: Union[str, None] = 'b357ef00886f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. ontology_nodes — no FK dependencies                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        'ontology_nodes',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('node_id', sa.String(length=128), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('domain', sa.String(length=64), nullable=False),
        sa.Column('parent_node_id', sa.String(length=128), nullable=True),
        sa.Column('is_leaf', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ontology_version', sa.String(length=20), nullable=False),
        sa.Column('schema_version', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('node_id', name='uq_ontology_nodes_node_id'),
    )
    op.create_index('ix_ontology_nodes_domain', 'ontology_nodes', ['domain'], unique=False)
    op.create_index('ix_ontology_nodes_parent', 'ontology_nodes', ['parent_node_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 2. behavior_patterns — FK → ontology_nodes                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        'behavior_patterns',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('pattern_id', sa.String(length=128), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('pattern_version', sa.String(length=20), nullable=False),
        sa.Column('ontology_node_id', sa.String(length=128), nullable=False),
        sa.Column('base_confidence', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('index_keys', sa.JSON(), nullable=False),
        sa.Column('rules', sa.JSON(), nullable=False),
        sa.Column('schema_version', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['ontology_node_id'], ['ontology_nodes.node_id'],
            ondelete='RESTRICT',
            name='fk_behavior_patterns_ontology_node',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pattern_id', 'pattern_version', name='uq_behavior_patterns_pid_ver'),
    )
    op.create_index('ix_behavior_patterns_ontology_node', 'behavior_patterns', ['ontology_node_id'], unique=False)
    op.create_index('ix_behavior_patterns_pattern_id', 'behavior_patterns', ['pattern_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 3. logic_signatures — FK → repositories, ontology_nodes            #
    # ------------------------------------------------------------------ #
    op.create_table(
        'logic_signatures',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.Uuid(), nullable=False),
        sa.Column('entity_seid', sa.String(length=64), nullable=False),
        sa.Column('entity_name', sa.String(length=512), nullable=False),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('primary_ontology_node_id', sa.String(length=128), nullable=True),
        sa.Column('overall_confidence', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['repository_id'], ['repositories.id'],
            ondelete='CASCADE',
            name='fk_logic_signatures_repository',
        ),
        sa.ForeignKeyConstraint(
            ['primary_ontology_node_id'], ['ontology_nodes.node_id'],
            ondelete='SET NULL',
            name='fk_logic_signatures_ontology_node',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repository_id', 'entity_seid', name='uq_logic_signatures_repo_seid'),
    )
    op.create_index('ix_logic_signatures_entity_seid', 'logic_signatures', ['entity_seid'], unique=False)
    op.create_index('ix_logic_signatures_entity_type', 'logic_signatures', ['entity_type'], unique=False)
    op.create_index('ix_logic_signatures_repository', 'logic_signatures', ['repository_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 4. logic_versions — FK → logic_signatures                          #
    # ------------------------------------------------------------------ #
    op.create_table(
        'logic_versions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('signature_id', sa.Uuid(), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('index_keys', sa.JSON(), nullable=False),
        sa.Column('ast_fingerprint', sa.String(length=64), nullable=True),
        sa.Column('complexity_score', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('line_start', sa.Integer(), nullable=True),
        sa.Column('line_end', sa.Integer(), nullable=True),
        sa.Column('raw_source_hash', sa.String(length=64), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['signature_id'], ['logic_signatures.id'],
            ondelete='CASCADE',
            name='fk_logic_versions_signature',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('signature_id', 'commit_hash', name='uq_logic_versions_sig_commit'),
    )
    op.create_index('ix_logic_versions_commit_hash', 'logic_versions', ['commit_hash'], unique=False)
    op.create_index('ix_logic_versions_signature', 'logic_versions', ['signature_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 5. logic_evidence — FK → logic_versions                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        'logic_evidence',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('version_id', sa.Uuid(), nullable=False),
        sa.Column('evidence_type', sa.String(length=64), nullable=False),
        sa.Column('pattern_id', sa.String(length=128), nullable=True),
        sa.Column('matched_text', sa.Text(), nullable=True),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('column_offset', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('weight', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['version_id'], ['logic_versions.id'],
            ondelete='CASCADE',
            name='fk_logic_evidence_version',
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_logic_evidence_evidence_type', 'logic_evidence', ['evidence_type'], unique=False)
    op.create_index('ix_logic_evidence_pattern_id', 'logic_evidence', ['pattern_id'], unique=False)
    op.create_index('ix_logic_evidence_version', 'logic_evidence', ['version_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 6. logic_transitions — FK → logic_versions (from + to)             #
    # ------------------------------------------------------------------ #
    op.create_table(
        'logic_transitions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('from_version_id', sa.Uuid(), nullable=True),
        sa.Column('to_version_id', sa.Uuid(), nullable=False),
        sa.Column('transition_type', sa.String(length=64), nullable=False),
        sa.Column('from_commit_hash', sa.String(length=40), nullable=True),
        sa.Column('to_commit_hash', sa.String(length=40), nullable=False),
        sa.Column('similarity_score', sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column('drift_magnitude', sa.Numeric(precision=6, scale=4), nullable=True),
        sa.Column('is_breaking_change', sa.Boolean(), nullable=False),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['from_version_id'], ['logic_versions.id'],
            ondelete='SET NULL',
            name='fk_logic_transitions_from_version',
        ),
        sa.ForeignKeyConstraint(
            ['to_version_id'], ['logic_versions.id'],
            ondelete='CASCADE',
            name='fk_logic_transitions_to_version',
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_logic_transitions_from_version', 'logic_transitions', ['from_version_id'], unique=False)
    op.create_index('ix_logic_transitions_to_commit', 'logic_transitions', ['to_commit_hash'], unique=False)
    op.create_index('ix_logic_transitions_to_version', 'logic_transitions', ['to_version_id'], unique=False)
    op.create_index('ix_logic_transitions_type', 'logic_transitions', ['transition_type'], unique=False)

    # ------------------------------------------------------------------ #
    # 7. behavior_explanations — FK → logic_versions                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        'behavior_explanations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('version_id', sa.Uuid(), nullable=False),
        sa.Column('explanation_type', sa.String(length=64), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('security_implications', sa.Text(), nullable=True),
        sa.Column('recommended_action', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('generated_by', sa.String(length=64), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['version_id'], ['logic_versions.id'],
            ondelete='CASCADE',
            name='fk_behavior_explanations_version',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version_id', 'explanation_type', name='uq_behavior_explanations_ver_type'),
    )
    op.create_index('ix_behavior_explanations_type', 'behavior_explanations', ['explanation_type'], unique=False)
    op.create_index('ix_behavior_explanations_version', 'behavior_explanations', ['version_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 8. behavior_drift — FK → logic_transitions, logic_versions         #
    # ------------------------------------------------------------------ #
    op.create_table(
        'behavior_drift',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('transition_id', sa.Uuid(), nullable=False),
        sa.Column('baseline_version_id', sa.Uuid(), nullable=False),
        sa.Column('current_version_id', sa.Uuid(), nullable=False),
        sa.Column('drift_score', sa.Numeric(precision=6, scale=4), nullable=False),
        sa.Column('drift_category', sa.String(length=64), nullable=False),
        sa.Column('ontology_shift', sa.Boolean(), nullable=False),
        sa.Column('from_ontology_node_id', sa.String(length=128), nullable=True),
        sa.Column('to_ontology_node_id', sa.String(length=128), nullable=True),
        sa.Column('pattern_additions', sa.JSON(), nullable=False),
        sa.Column('pattern_removals', sa.JSON(), nullable=False),
        sa.Column('pattern_modifications', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['transition_id'], ['logic_transitions.id'],
            ondelete='CASCADE',
            name='fk_behavior_drift_transition',
        ),
        sa.ForeignKeyConstraint(
            ['baseline_version_id'], ['logic_versions.id'],
            ondelete='CASCADE',
            name='fk_behavior_drift_baseline_version',
        ),
        sa.ForeignKeyConstraint(
            ['current_version_id'], ['logic_versions.id'],
            ondelete='CASCADE',
            name='fk_behavior_drift_current_version',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transition_id', name='uq_behavior_drift_transition'),
    )
    op.create_index('ix_behavior_drift_category', 'behavior_drift', ['drift_category'], unique=False)
    op.create_index('ix_behavior_drift_current_version', 'behavior_drift', ['current_version_id'], unique=False)
    op.create_index('ix_behavior_drift_transition', 'behavior_drift', ['transition_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 9. logic_clusters — no FK dependencies                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        'logic_clusters',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('cluster_key', sa.String(length=128), nullable=False),
        sa.Column('cluster_label', sa.String(length=256), nullable=True),
        sa.Column('ontology_node_id', sa.String(length=128), nullable=True),
        sa.Column('centroid_fingerprint', sa.String(length=64), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=False),
        sa.Column('cohesion_score', sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cluster_key', name='uq_logic_clusters_key'),
    )
    op.create_index('ix_logic_clusters_ontology_node', 'logic_clusters', ['ontology_node_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 10. logic_cluster_members — FK → logic_clusters, logic_signatures  #
    # ------------------------------------------------------------------ #
    op.create_table(
        'logic_cluster_members',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('cluster_id', sa.Uuid(), nullable=False),
        sa.Column('signature_id', sa.Uuid(), nullable=False),
        sa.Column('distance_to_centroid', sa.Numeric(precision=6, scale=4), nullable=True),
        sa.Column('is_centroid', sa.Boolean(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['cluster_id'], ['logic_clusters.id'],
            ondelete='CASCADE',
            name='fk_logic_cluster_members_cluster',
        ),
        sa.ForeignKeyConstraint(
            ['signature_id'], ['logic_signatures.id'],
            ondelete='CASCADE',
            name='fk_logic_cluster_members_signature',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cluster_id', 'signature_id', name='uq_logic_cluster_members_cls_sig'),
    )
    op.create_index('ix_logic_cluster_members_cluster', 'logic_cluster_members', ['cluster_id'], unique=False)
    op.create_index('ix_logic_cluster_members_signature', 'logic_cluster_members', ['signature_id'], unique=False)

    # ------------------------------------------------------------------ #
    # 11. logic_version_patterns — FK → logic_versions, behavior_patterns#
    # ------------------------------------------------------------------ #
    op.create_table(
        'logic_version_patterns',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('version_id', sa.Uuid(), nullable=False),
        sa.Column('behavior_pattern_id', sa.Uuid(), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('evidence_count', sa.Integer(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['version_id'], ['logic_versions.id'],
            ondelete='CASCADE',
            name='fk_logic_version_patterns_version',
        ),
        sa.ForeignKeyConstraint(
            ['behavior_pattern_id'], ['behavior_patterns.id'],
            ondelete='CASCADE',
            name='fk_logic_version_patterns_pattern',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version_id', 'behavior_pattern_id', name='uq_logic_version_patterns_ver_pat'),
    )
    op.create_index('ix_logic_version_patterns_behavior_pattern', 'logic_version_patterns', ['behavior_pattern_id'], unique=False)
    op.create_index('ix_logic_version_patterns_version', 'logic_version_patterns', ['version_id'], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order
    # 11
    op.drop_index('ix_logic_version_patterns_version', table_name='logic_version_patterns')
    op.drop_index('ix_logic_version_patterns_behavior_pattern', table_name='logic_version_patterns')
    op.drop_table('logic_version_patterns')

    # 10
    op.drop_index('ix_logic_cluster_members_signature', table_name='logic_cluster_members')
    op.drop_index('ix_logic_cluster_members_cluster', table_name='logic_cluster_members')
    op.drop_table('logic_cluster_members')

    # 9
    op.drop_index('ix_logic_clusters_ontology_node', table_name='logic_clusters')
    op.drop_table('logic_clusters')

    # 8
    op.drop_index('ix_behavior_drift_transition', table_name='behavior_drift')
    op.drop_index('ix_behavior_drift_current_version', table_name='behavior_drift')
    op.drop_index('ix_behavior_drift_category', table_name='behavior_drift')
    op.drop_table('behavior_drift')

    # 7
    op.drop_index('ix_behavior_explanations_version', table_name='behavior_explanations')
    op.drop_index('ix_behavior_explanations_type', table_name='behavior_explanations')
    op.drop_table('behavior_explanations')

    # 6
    op.drop_index('ix_logic_transitions_type', table_name='logic_transitions')
    op.drop_index('ix_logic_transitions_to_version', table_name='logic_transitions')
    op.drop_index('ix_logic_transitions_to_commit', table_name='logic_transitions')
    op.drop_index('ix_logic_transitions_from_version', table_name='logic_transitions')
    op.drop_table('logic_transitions')

    # 5
    op.drop_index('ix_logic_evidence_version', table_name='logic_evidence')
    op.drop_index('ix_logic_evidence_pattern_id', table_name='logic_evidence')
    op.drop_index('ix_logic_evidence_evidence_type', table_name='logic_evidence')
    op.drop_table('logic_evidence')

    # 4
    op.drop_index('ix_logic_versions_signature', table_name='logic_versions')
    op.drop_index('ix_logic_versions_commit_hash', table_name='logic_versions')
    op.drop_table('logic_versions')

    # 3
    op.drop_index('ix_logic_signatures_repository', table_name='logic_signatures')
    op.drop_index('ix_logic_signatures_entity_type', table_name='logic_signatures')
    op.drop_index('ix_logic_signatures_entity_seid', table_name='logic_signatures')
    op.drop_table('logic_signatures')

    # 2
    op.drop_index('ix_behavior_patterns_pattern_id', table_name='behavior_patterns')
    op.drop_index('ix_behavior_patterns_ontology_node', table_name='behavior_patterns')
    op.drop_table('behavior_patterns')

    # 1
    op.drop_index('ix_ontology_nodes_parent', table_name='ontology_nodes')
    op.drop_index('ix_ontology_nodes_domain', table_name='ontology_nodes')
    op.drop_table('ontology_nodes')
