"""Duplicate-publication detection for corpus candidate rows."""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

PUBLICATION_ID_FIELD = "publication_id"
TITLE_FIELD = "title"
DOI_FIELD = "doi"
YEAR_FIELD = "year"
SOURCE_URL_FIELD = "source_url"

_DOI_PREFIX_RE = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)
_VERSION_TRAILER_RE = re.compile(
    r"\b(?:preprint|accepted manuscript|author manuscript|version of record|vor)\b",
    re.IGNORECASE,
)
_PUNCTUATION_RE = re.compile(r"[^\w\s]")
_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class DuplicateCandidate:
    """Normalized corpus candidate fields used for duplicate detection."""

    publication_id: str
    title: str
    doi: str | None = None
    year: int | None = None
    source_url: str | None = None


@dataclass(frozen=True)
class DuplicatePublicationFlag:
    """Duplicate status for one candidate publication."""

    publication_id: str
    duplicate_set_id: str
    canonical_publication_id: str
    is_canonical: bool
    match_reasons: tuple[str, ...]


@dataclass(frozen=True)
class DuplicatePublicationSet:
    """A set of candidate rows that appear to describe the same publication."""

    duplicate_set_id: str
    canonical_publication_id: str
    publication_ids: tuple[str, ...]
    match_reasons: tuple[str, ...]
    flags: tuple[DuplicatePublicationFlag, ...]


def normalize_doi(value: str | None) -> str | None:
    """Normalize DOI variants to a lowercase DOI key."""

    if value is None:
        return None
    normalized = _DOI_PREFIX_RE.sub("", value.strip()).strip().lower()
    if not normalized:
        return None
    return normalized.rstrip(" .")


def normalize_title(value: str) -> str:
    """Normalize title text for duplicate matching."""

    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = _VERSION_TRAILER_RE.sub("", normalized)
    normalized = _PUNCTUATION_RE.sub(" ", normalized)
    normalized = _WHITESPACE_RE.sub(" ", normalized).strip()
    return normalized


def candidate_from_mapping(row: Mapping[str, object]) -> DuplicateCandidate:
    """Create a duplicate-detection candidate from a manifest-like mapping."""

    publication_id = _required_string(row, PUBLICATION_ID_FIELD)
    title = _required_string(row, TITLE_FIELD)
    return DuplicateCandidate(
        publication_id=publication_id,
        title=title,
        doi=normalize_doi(_optional_string(row, DOI_FIELD)),
        year=_optional_int(row, YEAR_FIELD),
        source_url=_optional_string(row, SOURCE_URL_FIELD),
    )


def detect_duplicate_publications(
    candidates: list[DuplicateCandidate],
) -> list[DuplicatePublicationSet]:
    """Detect duplicate publication candidates by DOI and title/version keys."""

    by_id = {candidate.publication_id: candidate for candidate in candidates}
    parent = {candidate.publication_id: candidate.publication_id for candidate in candidates}

    def find(publication_id: str) -> str:
        while parent[publication_id] != publication_id:
            parent[publication_id] = parent[parent[publication_id]]
            publication_id = parent[publication_id]
        return publication_id

    def union(left: str, right: str) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    reasons_by_pair: dict[frozenset[str], set[str]] = defaultdict(set)
    _union_by_key(candidates, lambda item: item.doi, "doi", union, reasons_by_pair)
    _union_by_key(
        candidates,
        lambda item: _title_year_key(item),
        "title_year",
        union,
        reasons_by_pair,
    )

    grouped: dict[str, list[str]] = defaultdict(list)
    for candidate in candidates:
        grouped[find(candidate.publication_id)].append(candidate.publication_id)

    duplicate_sets: list[DuplicatePublicationSet] = []
    for publication_ids in grouped.values():
        if len(publication_ids) < 2:
            continue
        sorted_ids = tuple(sorted(publication_ids))
        canonical_id = choose_canonical_publication(
            by_id[publication_id] for publication_id in sorted_ids
        )
        reasons = _reasons_for_set(sorted_ids, reasons_by_pair)
        duplicate_set_id = f"dup_{canonical_id}"
        flags = tuple(
            DuplicatePublicationFlag(
                publication_id=publication_id,
                duplicate_set_id=duplicate_set_id,
                canonical_publication_id=canonical_id,
                is_canonical=publication_id == canonical_id,
                match_reasons=reasons,
            )
            for publication_id in sorted_ids
        )
        duplicate_sets.append(
            DuplicatePublicationSet(
                duplicate_set_id=duplicate_set_id,
                canonical_publication_id=canonical_id,
                publication_ids=sorted_ids,
                match_reasons=reasons,
                flags=flags,
            )
        )
    return sorted(duplicate_sets, key=lambda item: item.duplicate_set_id)


def detect_duplicate_publications_from_csv(path: Path) -> list[DuplicatePublicationSet]:
    """Load corpus candidate rows from CSV and detect duplicate publications."""

    with path.open(encoding="utf-8", newline="") as handle:
        candidates = [candidate_from_mapping(row) for row in csv.DictReader(handle)]
    return detect_duplicate_publications(candidates)


def choose_canonical_publication(candidates: Iterable[DuplicateCandidate]) -> str:
    """Choose the canonical record for a duplicate set.

    Preference order is stable and provenance-preserving: lowest publication ID
    wins, so curation can keep the originally assigned corpus identifier.
    """

    candidate_list = list(candidates)
    if not candidate_list:
        raise ValueError("cannot choose canonical publication from an empty set")
    return min(candidate.publication_id for candidate in candidate_list)


def duplicate_flags_by_publication_id(
    duplicate_sets: list[DuplicatePublicationSet],
) -> dict[str, DuplicatePublicationFlag]:
    """Flatten duplicate-set flags by publication ID."""

    return {
        flag.publication_id: flag
        for duplicate_set in duplicate_sets
        for flag in duplicate_set.flags
    }


def _union_by_key(
    candidates: list[DuplicateCandidate],
    key_fn: Callable[[DuplicateCandidate], str | None],
    reason: str,
    union: Callable[[str, str], None],
    reasons_by_pair: dict[frozenset[str], set[str]],
) -> None:
    groups: dict[str, list[str]] = defaultdict(list)
    for candidate in candidates:
        key = key_fn(candidate)
        if key is not None:
            groups[key].append(candidate.publication_id)

    for publication_ids in groups.values():
        if len(publication_ids) < 2:
            continue
        first = publication_ids[0]
        for publication_id in publication_ids[1:]:
            union(first, publication_id)
            reasons_by_pair[frozenset({first, publication_id})].add(reason)


def _title_year_key(candidate: DuplicateCandidate) -> str | None:
    normalized_title = normalize_title(candidate.title)
    if not normalized_title or candidate.year is None:
        return None
    return f"{normalized_title}|{candidate.year}"


def _reasons_for_set(
    publication_ids: tuple[str, ...],
    reasons_by_pair: dict[frozenset[str], set[str]],
) -> tuple[str, ...]:
    reasons: set[str] = set()
    for index, left in enumerate(publication_ids):
        for right in publication_ids[index + 1 :]:
            reasons.update(reasons_by_pair.get(frozenset({left, right}), set()))
    return tuple(sorted(reasons))


def _required_string(row: Mapping[str, object], field: str) -> str:
    value = _optional_string(row, field)
    if value is None:
        raise ValueError(f"missing required field: {field}")
    return value


def _optional_string(row: Mapping[str, object], field: str) -> str | None:
    value = row.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    return value or None


def _optional_int(row: Mapping[str, object], field: str) -> int | None:
    value = _optional_string(row, field)
    if value is None:
        return None
    return int(value)
