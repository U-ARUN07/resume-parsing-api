"""Initial migration: create resumes table

Revision ID: 001_initial
Revises: 
Create Date: 2026-10-30 20:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'resumes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=10), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('extracted_data', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_resumes_id'), 'resumes', ['id'], unique=False)
    op.create_index(op.f('ix_resumes_stored_filename'), 'resumes', ['stored_filename'], unique=True)
    op.create_index(op.f('ix_resumes_file_type'), 'resumes', ['file_type'], unique=False)
    op.create_index(op.f('ix_resumes_created_at'), 'resumes', ['created_at'], unique=False)
    op.create_index('ix_resumes_file_type_created_at', 'resumes', ['file_type', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_resumes_file_type_created_at', table_name='resumes')
    op.drop_index(op.f('ix_resumes_created_at'), table_name='resumes')
    op.drop_index(op.f('ix_resumes_file_type'), table_name='resumes')
    op.drop_index(op.f('ix_resumes_stored_filename'), table_name='resumes')
    op.drop_index(op.f('ix_resumes_id'), table_name='resumes')
    op.drop_table('resumes')
