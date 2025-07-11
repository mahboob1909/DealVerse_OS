"""Add document processing fields

Revision ID: 004_add_document_processing_fields
Revises: 003_add_s3_storage_fields
Create Date: 2025-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_document_processing_fields'
down_revision = '003_add_s3_storage_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add enhanced document processing fields"""
    
    # Add processing status field
    op.add_column('documents', sa.Column('processing_status', sa.String(length=50), nullable=True, default='pending'))
    
    # Add enhanced metadata field
    op.add_column('documents', sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add text analysis results field
    op.add_column('documents', sa.Column('text_analysis', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add search keywords field
    op.add_column('documents', sa.Column('search_keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add processing artifacts paths
    op.add_column('documents', sa.Column('thumbnail_path', sa.String(length=500), nullable=True))
    op.add_column('documents', sa.Column('extracted_text_path', sa.String(length=500), nullable=True))
    op.add_column('documents', sa.Column('search_index_path', sa.String(length=500), nullable=True))
    
    # Set default values for existing records
    op.execute("UPDATE documents SET processing_status = 'pending' WHERE processing_status IS NULL")
    op.execute("UPDATE documents SET metadata = '{}' WHERE metadata IS NULL")
    op.execute("UPDATE documents SET text_analysis = '{}' WHERE text_analysis IS NULL")
    op.execute("UPDATE documents SET search_keywords = '[]' WHERE search_keywords IS NULL")


def downgrade():
    """Remove enhanced document processing fields"""
    
    # Remove processing artifacts paths
    op.drop_column('documents', 'search_index_path')
    op.drop_column('documents', 'extracted_text_path')
    op.drop_column('documents', 'thumbnail_path')
    
    # Remove processing fields
    op.drop_column('documents', 'search_keywords')
    op.drop_column('documents', 'text_analysis')
    op.drop_column('documents', 'metadata')
    op.drop_column('documents', 'processing_status')
