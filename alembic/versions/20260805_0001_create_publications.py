"""Create publications table for corpus metadata.

Revision ID: 20260805_0001
Revises:
Create Date: 2026-08-05

Publication table only — no passages, chunks, or embeddings (issue #27).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260805_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "publications",
        sa.Column("publication_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("license_status", sa.String(length=64), nullable=False),
        sa.Column("corpus_topic", sa.String(length=128), nullable=False),
        sa.Column(
            "ingestion_status",
            sa.String(length=64),
            server_default="not_ingested",
            nullable=False,
        ),
        sa.Column("doi", sa.String(length=256), nullable=True),
        sa.Column("pmcid", sa.String(length=64), nullable=True),
        sa.Column("pmid", sa.String(length=64), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("journal", sa.Text(), nullable=True),
        sa.Column("authors", sa.Text(), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("nasa_repository_id", sa.String(length=128), nullable=True),
        sa.Column("license", sa.String(length=64), nullable=True),
        sa.Column("pdf_path", sa.Text(), nullable=True),
        sa.Column("pdf_url", sa.Text(), nullable=True),
        sa.Column("fulltext_url", sa.Text(), nullable=True),
        sa.Column("organism_model", sa.String(length=128), nullable=True),
        sa.Column("exposure", sa.String(length=128), nullable=True),
        sa.Column("selection_notes", sa.Text(), nullable=True),
        sa.Column(
            "human_approval",
            sa.String(length=32),
            server_default="pending",
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
        sa.PrimaryKeyConstraint("publication_id"),
    )
    op.create_index("ix_publications_corpus_topic", "publications", ["corpus_topic"])
    op.create_index(
        "ix_publications_ingestion_status",
        "publications",
        ["ingestion_status"],
    )
    op.create_index("ix_publications_license_status", "publications", ["license_status"])
    op.create_index("ix_publications_doi", "publications", ["doi"])


def downgrade() -> None:
    op.drop_index("ix_publications_doi", table_name="publications")
    op.drop_index("ix_publications_license_status", table_name="publications")
    op.drop_index("ix_publications_ingestion_status", table_name="publications")
    op.drop_index("ix_publications_corpus_topic", table_name="publications")
    op.drop_table("publications")
