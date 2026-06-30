"""create phone number for user table

Revision ID: c19474cbaa93
Revises: 
Create Date: 2026-06-22 13:13:04.261441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c19474cbaa93'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users',sa.Column("phone_number",sa.String(),nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users','phone_number')
