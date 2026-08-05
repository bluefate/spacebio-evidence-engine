"""License classification and audit for controlled corpus candidates.

Implements the D10 license policy: CC BY is preferred; CC BY-NC-ND is allowed
because the evidence engine is non-commercial. Unknown, paywalled, or
incompatible licenses are blocked until human review.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "data" / "inventory" / "august_mvp_corpus_manifest.csv"


class LicenseStatus(StrEnum):
    """Disposition of a candidate license under the project use model."""

    ALLOWED = "allowed"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs_review"


@dataclass(frozen=True, slots=True)
class LicenseClassification:
    """Classification of a candidate publication license."""

    status: LicenseStatus
    can_ingest: bool
    access_restriction_notes: str
    redistribution_notes: str
    exclusion_flags: str


@dataclass(frozen=True, slots=True)
class AuditSummary:
    """Result of auditing the corpus manifest for licenses."""

    total: int
    allowed_count: int
    blocked_count: int
    needs_review_count: int
    rows: list[dict[str, str]]


_BY_VERSIONS = {
    "cc-by",
    "cc-by-4.0",
    "cc-by-3.0",
    "cc-by-2.0",
    "cc-by-2.5",
    "cc-by-1.0",
}

_BY_NC_ND_VERSIONS = {
    "cc-by-nc-nd",
    "cc-by-nc-nd-4.0",
    "cc-by-nc-nd-3.0",
    "cc-by-nc-nd-2.0",
    "cc-by-nc-nd-2.5",
    "cc-by-nc-nd-1.0",
}

_PUBLIC_DOMAIN = {"cc0", "cc-0", "public-domain", "pddl"}


def classify_license(license_id: str) -> LicenseClassification:
    """Return classification and notes for a license identifier.

    The identifier is normalized: lowercased and whitespace is collapsed to '-'.
    """
    normalized = license_id.strip().lower().replace(" ", "-")
    if not normalized:
        return _blocked("No license declared.")

    if normalized in _BY_VERSIONS:
        return _allowed(
            access_restriction_notes=(
                "Attribution (BY) required. Passages may be retrieved and quoted "
                "with citation and link to source."
            ),
            redistribution_notes=(
                "Passage quoting with source link is allowed. Full-text redistribution "
                "or derivative works require attribution; do not remove copyright notices."
            ),
        )

    if normalized in _BY_NC_ND_VERSIONS:
        return _allowed(
            access_restriction_notes=(
                "Attribution (BY), non-commercial (NC), and no-derivatives (ND) required. "
                "This project is non-commercial. Passages may be quoted with citation "
                "and link to source; do not create adapted full-text derivatives."
            ),
            redistribution_notes=(
                "Quote passages for non-commercial, citation-first answers. Do not sell "
                "the corpus, publish adapted full-text versions, or use the full text "
                "commercially. Re-review if the project later becomes commercial."
            ),
        )

    if normalized in _PUBLIC_DOMAIN:
        return _allowed(
            access_restriction_notes=(
                "No known copyright restrictions. Attribution is still good practice."
            ),
            redistribution_notes="No redistribution restrictions.",
        )

    if any(prefix in normalized for prefix in ("cc-by-sa", "cc-by-nc", "cc-by-nd")):
        return _needs_review(
            f"License variant '{license_id}' is not in the pre-approved allow-list. "
            "Requires human license review before ingest."
        )

    return _blocked(
        f"License '{license_id}' is paywalled, proprietary, or otherwise incompatible "
        "with the corpus use model. Exclude from ingest."
    )


def _allowed(*, access_restriction_notes: str, redistribution_notes: str) -> LicenseClassification:
    return LicenseClassification(
        status=LicenseStatus.ALLOWED,
        can_ingest=True,
        access_restriction_notes=access_restriction_notes,
        redistribution_notes=redistribution_notes,
        exclusion_flags="none",
    )


def _blocked(reason: str) -> LicenseClassification:
    return LicenseClassification(
        status=LicenseStatus.BLOCKED,
        can_ingest=False,
        access_restriction_notes=reason,
        redistribution_notes="Do not download or redistribute. Exclude from corpus.",
        exclusion_flags="blocked_license",
    )


def _needs_review(reason: str) -> LicenseClassification:
    return LicenseClassification(
        status=LicenseStatus.NEEDS_REVIEW,
        can_ingest=False,
        access_restriction_notes=reason,
        redistribution_notes="No redistribution until license is reviewed and approved.",
        exclusion_flags="blocked_license",
    )


def audit_manifest(path: Path | None = None) -> AuditSummary:
    """Read the corpus manifest and classify every row by license.

    Raises:
        ValueError: if required columns are missing.
    """
    path = path or MANIFEST_PATH
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        required = {"license", "exclusion_flags"}
        missing = required - set(fieldnames)
        if missing:
            raise ValueError(f"manifest missing columns: {sorted(missing)}")

        rows: list[dict[str, str]] = []
        allowed = blocked = needs_review = 0
        for row in reader:
            rows.append(row)
            classification = classify_license(row["license"])
            if classification.status == LicenseStatus.ALLOWED:
                allowed += 1
            elif classification.status == LicenseStatus.BLOCKED:
                blocked += 1
            else:
                needs_review += 1

    return AuditSummary(
        total=len(rows),
        allowed_count=allowed,
        blocked_count=blocked,
        needs_review_count=needs_review,
        rows=rows,
    )
