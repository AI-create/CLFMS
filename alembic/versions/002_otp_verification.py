"""Replace admin-approval with OTP email verification.

Revision ID: 002
Revises: 001
Create Date: 2026-04-20
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename is_approved → is_verified
    op.alter_column("users", "is_approved", new_column_name="is_verified")

    # Drop unique constraint on approval_token before rename
    op.drop_constraint("uq_users_approval_token", "users", type_="unique")

    # Rename approval_token → otp_code and clear any stored values (tokens ≠ OTPs)
    op.alter_column("users", "approval_token", new_column_name="otp_code")
    op.execute("UPDATE users SET otp_code = NULL")

    # Add OTP expiry column
    op.add_column("users", sa.Column("otp_expires_at", sa.DateTime(timezone=True), nullable=True))

    # All existing accounts stay verified
    op.execute("UPDATE users SET is_verified = true")


def downgrade() -> None:
    op.drop_column("users", "otp_expires_at")
    op.alter_column("users", "otp_code", new_column_name="approval_token")
    op.create_unique_constraint("uq_users_approval_token", "users", ["approval_token"])
    op.alter_column("users", "is_verified", new_column_name="is_approved")
