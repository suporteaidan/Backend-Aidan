"""rename users password to password_hash

Revision ID: 3739a11f965e
Revises: bb130666bb17
Create Date: 2026-10-28 10:16:39.709314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3739a11f965e'
down_revision: Union[str, Sequence[str], None] = 'bb130666bb17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "password",
        new_column_name="password_hash",
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "password_hash",
        new_column_name="password",
    )
