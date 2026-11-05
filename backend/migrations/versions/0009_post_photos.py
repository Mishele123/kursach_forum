"""Move existing cover photos into ordered post galleries."""
from alembic import op
import sqlalchemy as sa
revision = '0009'
down_revision = '0008'
branch_labels = depends_on = None


def upgrade():
    op.create_table('post_photos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(64), nullable=False, unique=True))
    op.create_index('ix_post_photos_post_id', 'post_photos', ['post_id'])
    op.execute("INSERT INTO post_photos (post_id, filename) SELECT id, photo_filename FROM posts WHERE photo_filename IS NOT NULL ORDER BY id")
    op.drop_column('posts', 'photo_filename')


def downgrade():
    op.add_column('posts', sa.Column('photo_filename', sa.String(64), nullable=True))
    op.execute("UPDATE posts SET photo_filename = (SELECT filename FROM post_photos WHERE post_id = posts.id ORDER BY id LIMIT 1)")
    op.drop_table('post_photos')
