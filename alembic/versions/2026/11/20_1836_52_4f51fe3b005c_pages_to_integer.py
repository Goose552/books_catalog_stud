"""pages to integer

Revision ID: 4f51fe3b005c
Revises: 603553cb4385
Create Date: 2026-11-20 18:36:52.691724

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4f51fe3b005c"
down_revision: Union[str, Sequence[str], None] = "603553cb4385"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "books",
        "pages",
        existing_type=sa.SMALLINT(),
        type_=sa.Integer(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "books",
        "pages",
        existing_type=sa.Integer(),
        type_=sa.SMALLINT(),
        existing_nullable=False,
    )
