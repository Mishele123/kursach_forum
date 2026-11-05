"""Create comments on publications."""
from alembic import op
import sqlalchemy as sa
revision = '0006'
down_revision = '0005'
branch_labels = depends_on = None


def upgrade():
    op.create_table('comments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('text', sa.String(3000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index('ix_comments_post_id_id', 'comments', ['post_id', 'id'])
    op.create_index('ix_comments_author_id', 'comments', ['author_id'])


def downgrade():
    op.drop_table('comments')
