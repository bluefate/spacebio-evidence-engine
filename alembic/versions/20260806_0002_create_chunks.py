"""Create chunks table for retrieval metadata.

Revision ID: 20260806_0002
Revises: 20260805_0001
Create Date: 2026-08-06

Chunk table with FK to publications (issue #33). No embeddings or passages.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260806_0002"
down_revision: str | Sequence[str] | None = "20260805_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "chunks",
        sa.Column("chunk_id", sa.String(length=64), nullable=False),
        sa.Column("publication_id", sa.String(length=64), nullable=False),
        sa.Column("section", sa.String(length=64), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=False),
        sa.Column("end_offset", sa.Integer(), nullable=False),
        sa.Column("chunking_strategy_version", sa.String(length=32), nullable=False),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column("passage_ids", sa.Text(), nullable=True),
        sa.Column("embedding_model", sa.String(length=128), nullable=True),
        sa.Column("section_heading", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["publication_id"],
            ["publications.publication_id"],
            name="fk_chunks_publication_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("chunk_id"),
    )
    op.create_index("ix_chunks_publication_id", "chunks", ["publication_id"])
    op.create_index("ix_chunks_section", "chunks", ["section"])
    op.create_index("ix_chunks_content_hash", "chunks", ["content_hash"])
    op.create_index(
        "ix_chunks_chunking_strategy_version",
        "chunks",
        ["chunking_strategy_version"],
    )


def downgrade() -> None:
    op.drop_index("ix_chunks_chunking_strategy_version", table_name="chunks")
    op.drop_index("ix_chunks_content_hash", table_name="chunks")
    op.drop_index("ix_chunks_section", table_name="chunks")
    op.drop_index("ix_chunks_publication_id", table_name="chunks")
    op.drop_table("chunks")
