"""License classification and corpus audit tests (issue #23)."""

from __future__ import annotations

import csv

from spacebio_evidence_engine.corpus import (
    LicenseStatus,
    audit_manifest,
    classify_license,
)
from spacebio_evidence_engine.corpus.licenses import MANIFEST_PATH


def test_cc_by_allowed() -> None:
    classification = classify_license("CC BY 4.0")
    assert classification.status == LicenseStatus.ALLOWED
    assert classification.can_ingest
    assert classification.exclusion_flags == "none"
    assert "Attribution" in classification.access_restriction_notes


def test_cc_by_nc_nd_allowed() -> None:
    classification = classify_license("CC BY-NC-ND 4.0")
    assert classification.status == LicenseStatus.ALLOWED
    assert classification.can_ingest
    assert "non-commercial" in classification.access_restriction_notes.lower()
    assert "no-derivatives" in classification.access_restriction_notes.lower()


def test_cc0_allowed() -> None:
    classification = classify_license("CC0")
    assert classification.status == LicenseStatus.ALLOWED
    assert classification.can_ingest
    assert classification.exclusion_flags == "none"


def test_cc_by_sa_needs_review() -> None:
    classification = classify_license("CC BY-SA 4.0")
    assert classification.status == LicenseStatus.NEEDS_REVIEW
    assert not classification.can_ingest
    assert classification.exclusion_flags == "blocked_license"


def test_paywalled_blocked() -> None:
    classification = classify_license("All rights reserved")
    assert classification.status == LicenseStatus.BLOCKED
    assert not classification.can_ingest
    assert classification.exclusion_flags == "blocked_license"


def test_empty_license_blocked() -> None:
    classification = classify_license("   ")
    assert classification.status == LicenseStatus.BLOCKED
    assert not classification.can_ingest


def test_unknown_license_blocked() -> None:
    classification = classify_license("custom-publisher-license")
    assert classification.status == LicenseStatus.BLOCKED
    assert not classification.can_ingest


def test_manifest_audit() -> None:
    summary = audit_manifest()
    assert summary.total == 23
    assert summary.allowed_count == 23
    assert summary.blocked_count == 0
    assert summary.needs_review_count == 0


def test_manifest_rows_have_license_notes() -> None:
    with MANIFEST_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    for row in rows:
        assert row["access_restriction_notes"]
        assert row["redistribution_notes"]
        assert row["exclusion_flags"] == "none"
        assert row["license"].lower() in {"cc-by", "cc-by-nc-nd"}
