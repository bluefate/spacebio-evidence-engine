"""Shared retrieval metadata filters (issue #47)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import Any

from sqlalchemy import Select
from sqlalchemy.sql import ColumnElement

from spacebio_evidence_engine.db.models import Chunk, Publication

# Approved filter keys mapped to publication/chunk metadata columns.
ALLOWED_FILTER_KEYS: frozenset[str] = frozenset(
    {
        "corpus_topic",
        "organism_model",
        "exposure",
        "publication_id",
        "section",
        "license_status",
        "year",
        "human_approval",
    }
)


class InvalidRetrievalFilterError(ValueError):
    """Raised when a retrieval filter key or value is invalid."""


@dataclass(frozen=True)
class RetrievalFilters:
    """Optional metadata filters applied before ranking (semantic or hybrid)."""

    corpus_topic: str | None = None
    organism_model: str | None = None
    exposure: str | None = None
    publication_id: str | None = None
    section: str | None = None
    license_status: str | None = None
    year: int | None = None
    human_approval: str | None = None

    def active_items(self) -> dict[str, str | int]:
        """Return only filters that are set (non-None)."""

        active: dict[str, str | int] = {}
        for item in fields(self):
            value = getattr(self, item.name)
            if value is not None:
                active[item.name] = value
        return active


# Backward-compatible alias used by semantic search (#44).
SemanticSearchFilters = RetrievalFilters


def parse_retrieval_filters(
    raw: Mapping[str, Any] | RetrievalFilters | None,
) -> RetrievalFilters | None:
    """Parse and validate filters from a mapping or existing dataclass.

    Unknown keys, blank strings, wrong types, and non-positive ``year`` values
    raise ``InvalidRetrievalFilterError``.
    """

    if raw is None:
        return None
    if isinstance(raw, RetrievalFilters):
        _validate_filter_values(raw)
        return raw

    unknown = sorted(set(raw) - ALLOWED_FILTER_KEYS)
    if unknown:
        raise InvalidRetrievalFilterError(
            "unknown retrieval filter key(s): "
            + ", ".join(unknown)
            + f"; allowed: {', '.join(sorted(ALLOWED_FILTER_KEYS))}"
        )

    kwargs: dict[str, Any] = {}
    for key in ALLOWED_FILTER_KEYS:
        if key not in raw:
            continue
        value = raw[key]
        if value is None:
            continue
        kwargs[key] = value

    filters = RetrievalFilters(**kwargs)
    _validate_filter_values(filters)
    if not filters.active_items():
        return None
    return filters


def apply_retrieval_filters(stmt: Select[Any], filters: RetrievalFilters | None) -> Select[Any]:
    """Apply validated metadata predicates to a Chunk/Publication select."""

    if filters is None:
        return stmt

    _validate_filter_values(filters)
    for predicate in _filter_predicates(filters):
        stmt = stmt.where(predicate)
    return stmt


def _validate_filter_values(filters: RetrievalFilters) -> None:
    for item in fields(filters):
        value = getattr(filters, item.name)
        if value is None:
            continue
        if item.name == "year":
            if not isinstance(value, int) or isinstance(value, bool):
                raise InvalidRetrievalFilterError("year filter must be an int")
            if value < 1:
                raise InvalidRetrievalFilterError("year filter must be >= 1")
            continue
        if not isinstance(value, str):
            raise InvalidRetrievalFilterError(f"{item.name} filter must be a string")
        if not value.strip():
            raise InvalidRetrievalFilterError(f"{item.name} filter must be a non-empty string")


def _filter_predicates(filters: RetrievalFilters) -> list[ColumnElement[bool]]:
    predicates: list[ColumnElement[bool]] = []
    if filters.corpus_topic is not None:
        predicates.append(Publication.corpus_topic == filters.corpus_topic)
    if filters.organism_model is not None:
        predicates.append(Publication.organism_model == filters.organism_model)
    if filters.exposure is not None:
        predicates.append(Publication.exposure == filters.exposure)
    if filters.publication_id is not None:
        predicates.append(Publication.publication_id == filters.publication_id)
    if filters.section is not None:
        predicates.append(Chunk.section == filters.section)
    if filters.license_status is not None:
        predicates.append(Publication.license_status == filters.license_status)
    if filters.year is not None:
        predicates.append(Publication.year == filters.year)
    if filters.human_approval is not None:
        predicates.append(Publication.human_approval == filters.human_approval)
    return predicates
