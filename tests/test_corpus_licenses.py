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


def test_cc_by_unversioned_allowed() -> None:
    classification = classify_license("CC BY")
    assert classification.status == LicenseStatus.ALLOWED
    assert classification.can_ingest


def test_cc_by_future_version_allowed() -> None:
    """New CC BY versions should not fall through to BLOCKED."""
    classification = classify_license("CC BY 5.0")
    assert classification.status == LicenseStatus.ALLOWED
    assert classification.can_ingest
    assert classification.exclusion_flags == "none"


def test_cc_by_nc_nd_allowed() -> None:
    classification = classify_license("CC BY-NC-ND 4.0")
    assert classification.status == LicenseStatus.ALLOWED
    assert classification.can_ingest
    assert "non-commercial" in classification.access_restriction_notes.lower()
    assert "no-derivatives" in classification.access_restriction_notes.lower()


def test_cc_by_nc_nd_future_version_allowed() -> None:
    classification = classify_license("CC BY-NC-ND 5.0")
    assert classification.status == LicenseStatus.ALLOWED
    assert classification.can_ingest


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


def test_cc_by_nc_needs_review() -> None:
    classification = classify_license("CC BY-NC 4.0")
    assert classification.status == LicenseStatus.NEEDS_REVIEW
    assert not classification.can_ingest


def test_paywalled_blocked() -> None:
    classification = classify_license("All rights reserved")
    assert classification.status == LicenseStatus.BLOCKED
    assert not classification.can_ingest
    assert classification.exclusion_flags == "blocked_license"


def test_empty_license_blocked() -> None:
    classification = classify_license("   ")
    assert classification.status == LicenseStatus.BLOCKED
    assert not classification.can_ingest


def test_unknown_cc_by_variant_needs_review() -> None:
    """Unknown CC BY-* variants should be reviewed, not mis-labeled as paywalled."""
    classification = classify_license("CC BY-Future-Variant 9.9")
    assert classification.status == LicenseStatus.NEEDS_REVIEW
    assert not classification.can_ingest
    assert "not in the pre-approved allow-list" in classification.access_restriction_notes


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


def test_manifest_license_audit_sample() -> None:
    """Spot-check sample rows against recorded license terms (issue #23 required audit)."""
    with MANIFEST_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["publication_id"]: row for row in rows}

    pub1 = by_id["pub_001"]
    assert pub1["license"] == "cc-by"
    assert pub1["exclusion_flags"] == "none"
    assert "Attribution" in pub1["access_restriction_notes"]
    assert "source link" in pub1["redistribution_notes"].lower()

    pub17 = by_id["pub_017"]
    assert pub17["license"] == "cc-by-nc-nd"
    assert pub17["exclusion_flags"] == "none"
    assert "non-commercial" in pub17["access_restriction_notes"].lower()
    assert "no-derivatives" in pub17["access_restriction_notes"].lower()
    assert "do not sell" in pub17["redistribution_notes"].lower()
