"""Optional place attached to a post."""
from alembic import op
import sqlalchemy as sa
revision = '0010'
down_revision = '0009'
branch_labels = depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('place_latitude', sa.Numeric(10, 7, asdecimal=False), nullable=True))
    op.add_column('posts', sa.Column('place_longitude', sa.Numeric(10, 7, asdecimal=False), nullable=True))
    op.add_column('posts', sa.Column('place_name', sa.String(200), nullable=True))
    op.create_check_constraint('ck_posts_place', 'posts',
        '(place_latitude IS NULL AND place_longitude IS NULL AND place_name IS NULL) OR (place_latitude BETWEEN -90 AND 90 AND place_longitude BETWEEN -180 AND 180)')


def downgrade():
    op.drop_constraint('ck_posts_place', 'posts', type_='check')
    op.drop_column('posts', 'place_name')
    op.drop_column('posts', 'place_longitude')
    op.drop_column('posts', 'place_latitude')
