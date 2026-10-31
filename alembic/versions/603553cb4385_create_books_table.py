"""Create books table

Revision ID: 603553cb4385
Revises: 
Create Date: 2026-10-28 21:22:26.147706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '603553cb4385'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('books',
    sa.Column('book_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=500), nullable=False),
    sa.Column('author', sa.VARCHAR(length=300), nullable=False),
    sa.Column('year', sa.SmallInteger(), nullable=False),
    sa.Column('genre', sa.VARCHAR(length=100), nullable=False),
    sa.Column('pages', sa.SmallInteger(), nullable=False),
    sa.Column('available', sa.Boolean(), nullable=False),
    sa.Column('isbn', sa.VARCHAR(length=20), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('extra', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('book_id'),
    sa.UniqueConstraint('isbn')
    )
    op.create_index(op.f('ix_books_author'), 'books', ['author'], unique=False)
    op.create_index(op.f('ix_books_available'), 'books', ['available'], unique=False)
    op.create_index(op.f('ix_books_genre'), 'books', ['genre'], unique=False)
    op.create_index(op.f('ix_books_title'), 'books', ['title'], unique=False)
    op.create_index(op.f('ix_books_year'), 'books', ['year'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_books_year'), table_name='books')
    op.drop_index(op.f('ix_books_title'), table_name='books')
    op.drop_index(op.f('ix_books_genre'), table_name='books')
    op.drop_index(op.f('ix_books_available'), table_name='books')
    op.drop_index(op.f('ix_books_author'), table_name='books')
    op.drop_table('books')

