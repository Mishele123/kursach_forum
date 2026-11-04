"""One like per user and publication."""
from alembic import op
import sqlalchemy as sa
revision = '0007'
down_revision = '0006'
branch_labels = depends_on = None


def upgrade():
    op.create_table('post_likes',
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True))
    op.create_index('ix_post_likes_user_id', 'post_likes', ['user_id'])


def downgrade():
    op.drop_table('post_likes')
