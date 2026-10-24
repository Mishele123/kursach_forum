"""Add a single photo to a post."""
from alembic import op
import sqlalchemy as sa
revision = '0003'
down_revision = '0002'
branch_labels = depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('photo_filename', sa.String(64), nullable=True))


def downgrade():
    op.drop_column('posts', 'photo_filename')
