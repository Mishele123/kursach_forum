"""Create bikes owned by users."""
from alembic import op
import sqlalchemy as sa
revision = '0005'
down_revision = '0004'
branch_labels = depends_on = None


def upgrade():
    op.create_table('bikes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('brand', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.CheckConstraint('year >= 1800 AND year <= 2200', name='ck_bikes_year'))
    op.create_index('ix_bikes_owner_id', 'bikes', ['owner_id'])


def downgrade():
    op.drop_table('bikes')
