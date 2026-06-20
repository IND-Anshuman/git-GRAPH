"""phase 7c decision intelligence

Revision ID: g7c
Revises: f1a2b3c4d5e6
Create Date: 2026-06-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g7c'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None

def upgrade():
    # 1. sa_decisions
    op.create_table('sa_decisions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('repository_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('decision_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('first_seen_commit', sa.String(length=40), nullable=True),
        sa.Column('last_seen_commit', sa.String(length=40), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decisions_repository_id', 'sa_decisions', ['repository_id'], unique=False)

    # 2. sa_decision_versions
    op.create_table('sa_decision_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('supporting_evidence', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['decision_id'], ['sa_decisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decision_versions_decision_id', 'sa_decision_versions', ['decision_id'], unique=False)

    # 3. sa_decision_evidence
    op.create_table('sa_decision_evidence',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('supporting_commits', sa.JSON(), nullable=True),
        sa.Column('supporting_documents', sa.JSON(), nullable=True),
        sa.Column('supporting_capabilities', sa.JSON(), nullable=True),
        sa.Column('supporting_architecture_changes', sa.JSON(), nullable=True),
        sa.Column('supporting_repository_events', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['decision_id'], ['sa_decisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decision_evidence_decision_id', 'sa_decision_evidence', ['decision_id'], unique=False)

    # 4. sa_decision_impacts
    op.create_table('sa_decision_impacts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('affected_capabilities', sa.JSON(), nullable=True),
        sa.Column('affected_architectures', sa.JSON(), nullable=True),
        sa.Column('affected_services', sa.JSON(), nullable=True),
        sa.Column('affected_dependencies', sa.JSON(), nullable=True),
        sa.Column('affected_ai_systems', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['decision_id'], ['sa_decisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decision_impacts_decision_id', 'sa_decision_impacts', ['decision_id'], unique=False)

    # 5. sa_decision_impact_timelines
    op.create_table('sa_decision_impact_timelines',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('entries', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['decision_id'], ['sa_decisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decision_impact_timelines_decision_id', 'sa_decision_impact_timelines', ['decision_id'], unique=False)

    # 6. sa_decision_dependencies
    op.create_table('sa_decision_dependencies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_decision_id', sa.String(length=36), nullable=False),
        sa.Column('target_decision_id', sa.String(length=36), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_decision_id'], ['sa_decisions.id'], ),
        sa.ForeignKeyConstraint(['target_decision_id'], ['sa_decisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decision_dependencies_source_decision_id', 'sa_decision_dependencies', ['source_decision_id'], unique=False)
    op.create_index('ix_sa_decision_dependencies_target_decision_id', 'sa_decision_dependencies', ['target_decision_id'], unique=False)

    # 7. sa_decision_conflicts
    op.create_table('sa_decision_conflicts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('decision_a_id', sa.String(length=36), nullable=False),
        sa.Column('decision_b_id', sa.String(length=36), nullable=False),
        sa.Column('conflict_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.Float(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['decision_a_id'], ['sa_decisions.id'], ),
        sa.ForeignKeyConstraint(['decision_b_id'], ['sa_decisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decision_conflicts_decision_a_id', 'sa_decision_conflicts', ['decision_a_id'], unique=False)
    op.create_index('ix_sa_decision_conflicts_decision_b_id', 'sa_decision_conflicts', ['decision_b_id'], unique=False)

    # 8. sa_decision_fitness
    op.create_table('sa_decision_fitness',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('longevity_score', sa.Float(), nullable=True),
        sa.Column('stability_score', sa.Float(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('adoption_score', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('overall_fitness', sa.Float(), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['decision_id'], ['sa_decisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decision_fitness_decision_id', 'sa_decision_fitness', ['decision_id'], unique=False)

    # 9. sa_decision_snapshots
    op.create_table('sa_decision_snapshots',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('repository_id', sa.String(length=255), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=True),
        sa.Column('decisions_json', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_decision_snapshots_repository_id', 'sa_decision_snapshots', ['repository_id'], unique=False)
    op.create_index('ix_sa_decision_snapshots_commit_hash', 'sa_decision_snapshots', ['commit_hash'], unique=False)

    # 10. sa_intents
    op.create_table('sa_intents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('repository_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('intent_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('supporting_decisions', sa.JSON(), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_intents_repository_id', 'sa_intents', ['repository_id'], unique=False)

    # 11. sa_intent_relationships
    op.create_table('sa_intent_relationships',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('intent_id', sa.String(length=36), nullable=False),
        sa.Column('decision_id', sa.String(length=36), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['decision_id'], ['sa_decisions.id'], ),
        sa.ForeignKeyConstraint(['intent_id'], ['sa_intents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_intent_relationships_decision_id', 'sa_intent_relationships', ['decision_id'], unique=False)
    op.create_index('ix_sa_intent_relationships_intent_id', 'sa_intent_relationships', ['intent_id'], unique=False)

    # 12. sa_repository_memory_events
    op.create_table('sa_repository_memory_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('repository_id', sa.String(length=255), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('commit_hash', sa.String(length=40), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_repository_memory_events_repository_id', 'sa_repository_memory_events', ['repository_id'], unique=False)

    # 13. sa_causal_relationships
    op.create_table('sa_causal_relationships',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('chain_id', sa.String(length=36), nullable=True),
        sa.Column('repository_id', sa.String(length=255), nullable=True),
        sa.Column('cause_id', sa.String(length=36), nullable=True),
        sa.Column('effect_id', sa.String(length=36), nullable=True),
        sa.Column('cause_label', sa.String(length=255), nullable=True),
        sa.Column('effect_label', sa.String(length=255), nullable=True),
        sa.Column('relationship_type', sa.String(length=50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sa_causal_relationships_chain_id', 'sa_causal_relationships', ['chain_id'], unique=False)
    op.create_index('ix_sa_causal_relationships_repository_id', 'sa_causal_relationships', ['repository_id'], unique=False)


def downgrade():
    op.drop_table('sa_causal_relationships')
    op.drop_table('sa_repository_memory_events')
    op.drop_table('sa_intent_relationships')
    op.drop_table('sa_intents')
    op.drop_table('sa_decision_snapshots')
    op.drop_table('sa_decision_fitness')
    op.drop_table('sa_decision_conflicts')
    op.drop_table('sa_decision_dependencies')
    op.drop_table('sa_decision_impact_timelines')
    op.drop_table('sa_decision_impacts')
    op.drop_table('sa_decision_evidence')
    op.drop_table('sa_decision_versions')
    op.drop_table('sa_decisions')
