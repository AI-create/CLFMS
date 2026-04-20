"""Add is_approved and approval_token columns to users table.

Revision ID: 001
Revises:
Create Date: 2026-04-20
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_approved", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("approval_token", sa.String(), nullable=True))
    op.create_unique_constraint("uq_users_approval_token", "users", ["approval_token"])

    # Mark all existing users as approved so current accounts aren't locked out
    op.execute("UPDATE users SET is_approved = true WHERE is_approved = false")


def downgrade() -> None:
    op.drop_constraint("uq_users_approval_token", "users", type_="unique")
    op.drop_column("users", "approval_token")
    op.drop_column("users", "is_approved")
