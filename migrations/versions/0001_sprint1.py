"""Initial relational schema for Sprint 1."""
from alembic import op
import sqlalchemy as sa

revision = "0001_sprint1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("username_key", sa.String(150), nullable=False, unique=True),
        sa.Column("email", sa.String(254)),
        sa.Column("email_key", sa.String(254), unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("avatar_url", sa.Text()),
        sa.Column("bio", sa.String(1000)),
        sa.Column("is_banned", sa.Boolean(), nullable=False),
        sa.Column("city", sa.String(100)),
        sa.Column("discipline", sa.String(100)),
        sa.Column("interests", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("email_verified_at", sa.DateTime(timezone=True)),
        sa.Column("last_password_change", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table("posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("photo_url", sa.Text()),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(trim(title)) > 0", name="post_title_not_blank"),
        sa.CheckConstraint("length(trim(text)) > 0", name="post_text_not_blank"),
    )
    op.create_index("ix_posts_author_id", "posts", ["author_id"])
    op.create_index("ix_posts_created_id", "posts", ["created_at", "id"])
    op.create_index("ix_posts_category_created", "posts", ["category", "created_at"])
    op.create_table("bikes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(trim(brand)) > 0", name="bike_brand_not_blank"),
        sa.CheckConstraint("length(trim(model)) > 0", name="bike_model_not_blank"),
        sa.CheckConstraint("year >= 1800", name="bike_year_min"),
    )
    op.create_index("ix_bikes_user_id", "bikes", ["user_id"])


def downgrade():
    op.drop_table("bikes")
    op.drop_table("posts")
    op.drop_table("users")
