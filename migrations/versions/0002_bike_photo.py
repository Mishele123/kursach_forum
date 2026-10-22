"""Add an optional bicycle photo without changing existing bikes."""
from alembic import op
import sqlalchemy as sa

revision = "0002_bike_photo"
down_revision = "0001_sprint1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("bikes", sa.Column("photo_url", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("bikes", "photo_url")
