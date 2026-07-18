"""Add student accounts, activation codes and refresh sessions."""

from alembic import op
import sqlalchemy as sa

from backend.models import AccountActivationToken, RefreshToken


revision = "20260718_0002"
down_revision = "20260718_0001"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    return {item["name"] for item in sa.inspect(op.get_bind()).get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    return {item["name"] for item in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    user_columns = _columns("users")
    additions = {
        "username": sa.Column("username", sa.String(30), nullable=True),
        "failed_login_count": sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"),
        "locked_until": sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        "last_login_at": sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        "updated_at": sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    }
    for name, column in additions.items():
        if name not in user_columns:
            op.add_column("users", column)
    if "ix_users_username" not in _indexes("users"):
        op.create_index("ix_users_username", "users", ["username"], unique=True)

    if "user_id" not in _columns("students"):
        op.add_column("students", sa.Column("user_id", sa.String(36), nullable=True))
        if op.get_bind().dialect.name == "postgresql":
            op.create_foreign_key("fk_students_user_id", "students", "users", ["user_id"], ["id"])
    if "ix_students_user_id" not in _indexes("students"):
        op.create_index("ix_students_user_id", "students", ["user_id"], unique=True)

    RefreshToken.__table__.create(bind=op.get_bind(), checkfirst=True)
    AccountActivationToken.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    AccountActivationToken.__table__.drop(bind=op.get_bind(), checkfirst=True)
    RefreshToken.__table__.drop(bind=op.get_bind(), checkfirst=True)
    with op.batch_alter_table("students") as batch:
        batch.drop_index("ix_students_user_id")
        batch.drop_column("user_id")
    with op.batch_alter_table("users") as batch:
        batch.drop_index("ix_users_username")
        for column in ("updated_at", "last_login_at", "locked_until", "failed_login_count", "username"):
            batch.drop_column(column)
