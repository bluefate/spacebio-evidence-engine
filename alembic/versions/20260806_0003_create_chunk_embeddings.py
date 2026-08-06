"""Create chunk_embeddings table with pgvector column.

Revision ID: 20260806_0003
Revises: 20260806_0002
Create Date: 2026-08-06

Vector storage for chunk embeddings (issue #42). Requires the PostgreSQL
``vector`` extension (issue #8). SQLite uses JSON text for CI-only upgrades.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260806_0003"
down_revision: str | Sequence[str] | None = "20260806_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MVP_EMBEDDING_DIMENSION = 384


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
        from pgvector.sqlalchemy import Vector

        embedding_type: sa.types.TypeEngine[object] = Vector(MVP_EMBEDDING_DIMENSION)
    else:
        # CI / SQLite: JSON-encoded float list standing in for vector(N).
        embedding_type = sa.Text()

    op.create_table(
        "chunk_embeddings",
        sa.Column("chunk_id", sa.String(length=64), nullable=False),
        sa.Column("embedding", embedding_type, nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column(
            "dimension",
            sa.Integer(),
            server_default=str(MVP_EMBEDDING_DIMENSION),
            nullable=False,
        ),
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
        sa.CheckConstraint(
            f"dimension = {MVP_EMBEDDING_DIMENSION}",
            name="ck_chunk_embeddings_dimension_mvp",
        ),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["chunks.chunk_id"],
            name="fk_chunk_embeddings_chunk_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("chunk_id"),
    )
    op.create_index("ix_chunk_embeddings_model_name", "chunk_embeddings", ["model_name"])


def downgrade() -> None:
    op.drop_index("ix_chunk_embeddings_model_name", table_name="chunk_embeddings")
    op.drop_table("chunk_embeddings")
