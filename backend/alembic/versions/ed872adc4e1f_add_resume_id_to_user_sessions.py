"""
drop completeness_summary column from resumes table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ed872adc4e1f'
down_revision = '327a267b6293'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('resumes', 'completeness_summary')

def downgrade():
    op.add_column('resumes', sa.Column('completeness_summary', sa.JSON(), nullable=True)) 