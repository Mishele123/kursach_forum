"""Create posts for the community feed."""
from alembic import op
import sqlalchemy as sa
revision = '0002'
down_revision = '0001'
branch_labels = depends_on = None


def upgrade():
    op.create_table('posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('text', sa.String(10000), nullable=False),
        sa.Column('category', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("category IN ('maintenance', 'upgrade', 'route', 'tricks')", name='ck_posts_category'))
    op.create_index('ix_posts_author_id', 'posts', ['author_id'])
    op.create_index('ix_posts_created_id', 'posts', ['created_at', 'id'])


def downgrade():
    op.drop_table('posts')
