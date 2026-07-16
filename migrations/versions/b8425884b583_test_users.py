"""test_users

Revision ID: b8425884b583
Revises: a1d35dae35b2
Create Date: 2026-07-16 13:54:40.212972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime
from app.hashing import get_password_hash


# revision identifiers, used by Alembic.
revision: str = 'b8425884b583'
down_revision: Union[str, None] = 'a1d35dae35b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    admin_password = get_password_hash("admin123")
    user_password = get_password_hash("user123")

    connection.execute(
        sa.text("""
            INSERT INTO admins (email, full_name, hashed_password, is_active, created_at, updated_at)
            VALUES (:email, :full_name, :hashed_password, :is_active, :created_at, :updated_at)
        """),
        {
            "email": "admin@test.com",
            "full_name": "Admin User",
            "hashed_password": admin_password,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    )

    connection.execute(
        sa.text("""
            INSERT INTO users (email, full_name, hashed_password, is_active, created_at, updated_at)
            VALUES (:email, :full_name, :hashed_password, :is_active, :created_at, :updated_at)
        """),
        {
            "email": "user@test.com",
            "full_name": "Test User",
            "hashed_password": user_password,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    )

    result = connection.execute(
        sa.text("SELECT id FROM users WHERE email = 'user@test.com'")
    )
    user_id = result.scalar()

    connection.execute(
        sa.text("""
            INSERT INTO accounts (user_id, balance, created_at, updated_at)
            VALUES (:user_id, :balance, :created_at, :updated_at)
        """),
        {
            "user_id": user_id,
            "balance": 0.00,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text("DELETE FROM accounts WHERE user_id = (SELECT id FROM users WHERE email = 'user@test.com')")
    )
    connection.execute(
        sa.text("DELETE FROM users WHERE email = 'user@test.com'")
    )
    connection.execute(
        sa.text("DELETE FROM admins WHERE email = 'admin@test.com'")
    )