"""Add full-text search tsvector column to chunks.

Revision ID: 20260811_0004
Revises: 20260806_0003
Create Date: 2026-08-11

PostgreSQL full-text search (issue #45). SQLite CI uses a plain text
stand-in because ``tsvector`` is not available.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision: str = "20260811_0004"
down_revision: str | Sequence[str] | None = "20260806_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.add_column(
            "chunks",
            sa.Column(
                "search_tsv",
                TSVECTOR,
                sa.Computed("to_tsvector('english', chunk_text)", persisted=True),
                nullable=False,
            ),
        )
        op.create_index(
            "ix_chunks_search_tsv",
            "chunks",
            ["search_tsv"],
            postgresql_using="gin",
        )
    else:
        op.add_column(
            "chunks",
            sa.Column("search_tsv", sa.Text(), nullable=True),
        )
        op.create_index("ix_chunks_search_tsv", "chunks", ["chunk_text"])


def downgrade() -> None:
    op.drop_index("ix_chunks_search_tsv", table_name="chunks")
    op.drop_column("chunks", "search_tsv")
