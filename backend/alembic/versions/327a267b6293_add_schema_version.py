"""add_schema_version

Revision ID: 327a267b6293
Revises: e905398f7c54
Create Date: 2025-07-20 16:16:59.153050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '327a267b6293'
down_revision = 'e905398f7c54'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add schema_version column to resumes table
    op.add_column('resumes', sa.Column('schema_version', sa.String(50), nullable=True))
    
    # Set default schema version for existing resumes
    op.execute("UPDATE resumes SET schema_version = 'v1.0.0' WHERE schema_version IS NULL")
    
    # Make schema_version not nullable after setting defaults
    op.alter_column('resumes', 'schema_version', nullable=False)


def downgrade() -> None:
    op.drop_column('resumes', 'schema_version') 