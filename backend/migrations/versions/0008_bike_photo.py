"""Bike photograph; users already have avatar_url."""
from alembic import op
import sqlalchemy as sa
revision = '0008'
down_revision = '0007'
branch_labels = depends_on = None


def upgrade():
    op.add_column('bikes', sa.Column('photo_filename', sa.String(64), nullable=True))


def downgrade():
    op.drop_column('bikes', 'photo_filename')
