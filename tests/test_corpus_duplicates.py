"""Tests for corpus candidate duplicate detection (issue #24)."""

from __future__ import annotations

import csv
from pathlib import Path

from spacebio_evidence_engine.corpus.duplicates import (
    candidate_from_mapping,
    detect_duplicate_publications,
    detect_duplicate_publications_from_csv,
    duplicate_flags_by_publication_id,
    normalize_doi,
    normalize_title,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "inventory" / "august_mvp_corpus_manifest.csv"


def test_normalize_doi_handles_url_prefix_case_and_trailing_punctuation() -> None:
    assert normalize_doi("https://doi.org/10.1038/S41526-024-00406-3.") == (
        "10.1038/s41526-024-00406-3"
    )
    assert normalize_doi("doi: 10.3390/CELLS13242120") == "10.3390/cells13242120"
    assert normalize_doi("   ") is None


def test_normalize_title_handles_punctuation_accents_and_version_trailers() -> None:
    assert normalize_title("Estrogen Receptor Alpha (ERα): Version of Record") == (
        "estrogen receptor alpha er"
    )


def test_detects_doi_duplicates_and_preserves_canonical_record() -> None:
    candidates = [
        candidate_from_mapping(
            {
                "publication_id": "pub_010",
                "title": "Canonical paper",
                "doi": "10.1000/example",
                "year": "2024",
                "source_url": "https://doi.org/10.1000/example",
            }
        ),
        candidate_from_mapping(
            {
                "publication_id": "pub_011",
                "title": "Different title variant",
                "doi": "https://doi.org/10.1000/EXAMPLE",
                "year": "2024",
                "source_url": "https://doi.org/10.1000/example",
            }
        ),
    ]

    duplicate_sets = detect_duplicate_publications(candidates)

    assert len(duplicate_sets) == 1
    duplicate_set = duplicate_sets[0]
    assert duplicate_set.canonical_publication_id == "pub_010"
    assert duplicate_set.publication_ids == ("pub_010", "pub_011")
    assert duplicate_set.match_reasons == ("doi",)
    flags = duplicate_flags_by_publication_id(duplicate_sets)
    assert flags["pub_010"].is_canonical
    assert not flags["pub_011"].is_canonical
    assert flags["pub_011"].canonical_publication_id == "pub_010"


def test_detects_title_year_version_variants_when_doi_is_missing() -> None:
    candidates = [
        candidate_from_mapping(
            {
                "publication_id": "pub_020",
                "title": "Microgravity Accelerates Skeletal Muscle Degeneration",
                "doi": "",
                "year": "2025",
            }
        ),
        candidate_from_mapping(
            {
                "publication_id": "pub_021",
                "title": "Microgravity accelerates skeletal muscle degeneration: preprint",
                "doi": "",
                "year": "2025",
            }
        ),
    ]

    duplicate_sets = detect_duplicate_publications(candidates)

    assert len(duplicate_sets) == 1
    assert duplicate_sets[0].canonical_publication_id == "pub_020"
    assert duplicate_sets[0].match_reasons == ("title_year",)


def test_current_august_manifest_has_no_duplicate_candidates() -> None:
    duplicate_sets = detect_duplicate_publications_from_csv(MANIFEST)
    assert duplicate_sets == []


def test_manifest_doi_keys_are_unique_after_normalization() -> None:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    doi_keys = [normalize_doi(row["doi"]) for row in rows]
    assert len(doi_keys) == len(set(doi_keys))
