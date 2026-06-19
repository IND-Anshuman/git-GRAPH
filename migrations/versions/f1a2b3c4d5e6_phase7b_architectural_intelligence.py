"""phase7b_architectural_intelligence

Revision ID: f1a2b3c4d5e6
Revises: e2088bcbd852
Create Date: 2026-06-19 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e2088bcbd852'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. architecture_profiles
    op.create_table('architecture_profiles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('architecture_type', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('confidence', sa.JSON(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_profiles_repo', 'architecture_profiles', ['repository_id'], unique=False)
    op.create_index('ix_architecture_profiles_repo_commit', 'architecture_profiles', ['repository_id', 'commit_hash'], unique=False)

    # 2. architecture_snapshots
    op.create_table('architecture_snapshots',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('architecture_profiles', sa.JSON(), nullable=False),
        sa.Column('fitness_metrics', sa.JSON(), nullable=False),
        sa.Column('violations', sa.JSON(), nullable=False),
        sa.Column('ownership_profile', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_snapshots_repo', 'architecture_snapshots', ['repository_id'], unique=False)
    op.create_index('ix_architecture_snapshots_repo_commit', 'architecture_snapshots', ['repository_id', 'commit_hash'], unique=False)

    # 3. architecture_fitness
    op.create_table('architecture_fitness',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('coupling_score', sa.Float(), nullable=False),
        sa.Column('cohesion_score', sa.Float(), nullable=False),
        sa.Column('instability_score', sa.Float(), nullable=False),
        sa.Column('abstractness_score', sa.Float(), nullable=False),
        sa.Column('distance_from_main_sequence', sa.Float(), nullable=False),
        sa.Column('cyclicity_score', sa.Float(), nullable=False),
        sa.Column('layer_violation_score', sa.Float(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('formulas', sa.JSON(), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_fitness_repo', 'architecture_fitness', ['repository_id'], unique=False)

    # 4. architecture_violations
    op.create_table('architecture_violations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('rule_name', sa.String(length=256), nullable=False),
        sa.Column('severity', sa.String(length=64), nullable=False),
        sa.Column('affected_entities', sa.JSON(), nullable=False),
        sa.Column('affected_capabilities', sa.JSON(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_violations_repo', 'architecture_violations', ['repository_id'], unique=False)

    # 5. architecture_invariants
    op.create_table('architecture_invariants',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=True),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('rule_expression', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=64), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('source_role', sa.String(length=128), nullable=True),
        sa.Column('forbidden_target_role', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_invariants_repo', 'architecture_invariants', ['repository_id'], unique=False)

    # 6. architecture_drifts
    op.create_table('architecture_drifts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('drift_type', sa.String(length=64), nullable=False),
        sa.Column('previous_state', sa.JSON(), nullable=False),
        sa.Column('current_state', sa.JSON(), nullable=False),
        sa.Column('delta', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('from_commit', sa.String(length=40), nullable=False),
        sa.Column('to_commit', sa.String(length=40), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_drifts_repo', 'architecture_drifts', ['repository_id'], unique=False)

    # 7. architecture_timelines
    op.create_table('architecture_timelines',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('entries', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_timelines_repo', 'architecture_timelines', ['repository_id'], unique=False)

    # 8. architecture_benchmarks
    op.create_table('architecture_benchmarks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('current_fitness', sa.Float(), nullable=False),
        sa.Column('comparison_group', sa.String(length=256), nullable=False),
        sa.Column('comparison_avg_fitness', sa.Float(), nullable=False),
        sa.Column('percentile_rank', sa.Float(), nullable=False),
        sa.Column('key_gaps', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_benchmarks_repo', 'architecture_benchmarks', ['repository_id'], unique=False)

    # 9. architecture_similarities
    op.create_table('architecture_similarities',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('source_repository_id', sa.String(length=256), nullable=False),
        sa.Column('target_repository_id', sa.String(length=256), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('topology_similarity', sa.Float(), nullable=False),
        sa.Column('dependency_similarity', sa.Float(), nullable=False),
        sa.Column('capability_similarity', sa.Float(), nullable=False),
        sa.Column('flow_similarity', sa.Float(), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_similarities_source', 'architecture_similarities', ['source_repository_id'], unique=False)
    op.create_index('ix_architecture_similarities_target', 'architecture_similarities', ['target_repository_id'], unique=False)

    # 10. ownership_profiles
    op.create_table('ownership_profiles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('capability_ownership', sa.JSON(), nullable=False),
        sa.Column('knowledge_silos', sa.JSON(), nullable=False),
        sa.Column('bus_factor_risks', sa.JSON(), nullable=False),
        sa.Column('unowned_capabilities', sa.JSON(), nullable=False),
        sa.Column('overloaded_teams', sa.JSON(), nullable=False),
        sa.Column('ownership_drift', sa.JSON(), nullable=False),
        sa.Column('evidence_sources', sa.JSON(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ownership_profiles_repo', 'ownership_profiles', ['repository_id'], unique=False)

    # 11. refactoring_candidates
    op.create_table('refactoring_candidates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('candidate_type', sa.String(length=64), nullable=False),
        sa.Column('priority', sa.String(length=64), nullable=False),
        sa.Column('target_entities', sa.JSON(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('expected_benefit', sa.Text(), nullable=False),
        sa.Column('fitness_impact', sa.Float(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_refactoring_candidates_repo', 'refactoring_candidates', ['repository_id'], unique=False)

    # 12. architecture_recommendations
    op.create_table('architecture_recommendations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('repository_id', sa.String(length=256), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('recommendation_type', sa.String(length=64), nullable=False),
        sa.Column('target_elements', sa.JSON(), nullable=False),
        sa.Column('action_description', sa.Text(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('expected_fitness_delta', sa.Float(), nullable=False),
        sa.Column('difficulty', sa.String(length=64), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_architecture_recommendations_repo', 'architecture_recommendations', ['repository_id'], unique=False)


def downgrade() -> None:
    op.drop_table('architecture_recommendations')
    op.drop_table('refactoring_candidates')
    op.drop_table('ownership_profiles')
    op.drop_table('architecture_similarities')
    op.drop_table('architecture_benchmarks')
    op.drop_table('architecture_timelines')
    op.drop_table('architecture_drifts')
    op.drop_table('architecture_invariants')
    op.drop_table('architecture_violations')
    op.drop_table('architecture_fitness')
    op.drop_table('architecture_snapshots')
    op.drop_table('architecture_profiles')
