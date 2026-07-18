"""Create the complete adaptive tutoring platform schema."""

from alembic import op

from backend.models import Base


revision = "20260718_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # checkfirst makes this baseline safe for existing SQLite pilots.
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=True)
