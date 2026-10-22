"""Track bundled examples without changing existing accounts or posts."""
from alembic import op
import sqlalchemy as sa

revision = "0003_demo_keys"
down_revision = "0002_bike_photo"
branch_labels = None
depends_on = None


def upgrade():
    for table in ("users", "posts"):
        op.add_column(table, sa.Column("demo_key", sa.String(64), nullable=True))
        op.create_index(f"ix_{table}_demo_key", table, ["demo_key"], unique=True)


def downgrade():
    for table in ("posts", "users"):
        op.drop_index(f"ix_{table}_demo_key", table_name=table)
        op.drop_column(table, "demo_key")
