"""Add cycling profile fields."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
revision = '0004'
down_revision = '0003'
branch_labels = depends_on = None


def upgrade():
    op.add_column('users', sa.Column('city', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('discipline', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('interests', JSONB(), nullable=False, server_default='[]'))


def downgrade():
    op.drop_column('users', 'interests')
    op.drop_column('users', 'discipline')
    op.drop_column('users', 'city')
