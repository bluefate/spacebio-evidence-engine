"""Register local-extra publications from a DOI or uploaded PDF (issue #165).

Ad-hoc papers are stored as ``local_*`` IDs with ``corpus_topic=local_extras``
and ``human_approval=pending``. They are **not** added to the approved 23-paper
MVP inventory. Paywalled / blocked licenses are rejected. PDFs are stored
through ``LocalFileStorage`` and never executed.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session

from spacebio_evidence_engine.corpus.licenses import LicenseStatus, classify_license
from spacebio_evidence_engine.db.models import Publication
from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.indexing import index_chunk_embeddings
from spacebio_evidence_engine.ingestion.reprocess import reprocess_publication
from spacebio_evidence_engine.ingestion.status import IngestionStatus
from spacebio_evidence_engine.storage.local import LocalFileStorage

LOCAL_EXTRAS_TOPIC = "local_extras"
PDF_MAGIC = b"%PDF"
_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
_CROSSREF = "https://api.crossref.org/works/{doi}"
_USER_AGENT = "spacebio-evidence-engine/0.1 (local extras register; mailto:unused@localhost)"


class RegisterError(ValueError):
    """Raised when registration is rejected (license, file type, DOI)."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


class HttpFetcher(Protocol):
    """Injectable HTTP GET for tests."""

    def get_json(self, url: str) -> dict[str, Any]: ...

    def get_bytes(self, url: str) -> tuple[bytes, str]: ...


@dataclass(frozen=True, slots=True)
class RegisterResult:
    """Outcome of registering one local-extra publication."""

    publication_id: str
    doi: str | None
    title: str
    license: str
    license_status: str
    human_approval: str
    corpus_topic: str
    pdf_stored: bool
    collection: str = "local_extras"


class UrllibFetcher:
    """stdlib HTTP client with a timeout."""

    def __init__(self, timeout_s: float = 20.0) -> None:
        self._timeout_s = timeout_s

    def get_json(self, url: str) -> dict[str, Any]:
        body, _content_type = self.get_bytes(url)
        parsed: object = json.loads(body.decode("utf-8"))
        if not isinstance(parsed, dict):
            raise RegisterError("metadata response was not a JSON object", status_code=502)
        return parsed

    def get_bytes(self, url: str) -> tuple[bytes, str]:
        request = Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "*/*"})
        try:
            with urlopen(request, timeout=self._timeout_s) as response:
                content_type = str(response.headers.get("Content-Type") or "")
                return response.read(), content_type
        except HTTPError as exc:
            raise RegisterError(f"HTTP {exc.code} fetching {url}", status_code=502) from exc
        except URLError as exc:
            raise RegisterError(
                f"network error fetching URL: {exc.reason}",
                status_code=502,
            ) from exc


def normalize_doi(raw: str) -> str:
    value = raw.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = value.strip().strip("/")
    if not _DOI_RE.match(value):
        raise RegisterError("DOI must look like 10.xxxx/...")
    return value


def license_id_from_url(url: str) -> str:
    lowered = url.strip().lower()
    if "creativecommons.org/publicdomain" in lowered or "/publicdomain/zero" in lowered:
        return "cc0"
    if "creativecommons.org/licenses/by-nc-nd" in lowered:
        return "cc-by-nc-nd"
    if "creativecommons.org/licenses/by-nc" in lowered:
        return "cc-by-nc"
    if "creativecommons.org/licenses/by-nd" in lowered:
        return "cc-by-nd"
    if "creativecommons.org/licenses/by-sa" in lowered:
        return "cc-by-sa"
    if "creativecommons.org/licenses/by" in lowered:
        return "cc-by"
    return url.strip() or "unknown"


def is_pdf_bytes(data: bytes) -> bool:
    return data[:4] == PDF_MAGIC


def local_publication_id(*, doi: str | None, title: str, extra: str = "") -> str:
    digest = hashlib.sha256(f"{doi or ''}|{title}|{extra}".encode()).hexdigest()[:12]
    return f"local_{digest}"


def persist_pdf(storage: LocalFileStorage, publication_id: str, data: bytes) -> str:
    if not is_pdf_bytes(data):
        raise RegisterError("file is not a PDF", status_code=400)
    return storage.put(publication_id, f"{publication_id}.pdf", data)


def _upsert_publication(
    session: Session,
    *,
    publication_id: str,
    title: str,
    doi: str | None,
    license_id: str,
    classification_status: LicenseStatus,
    source_url: str,
    pdf_url: str | None,
    pdf_path: str | None,
    organism_model: str | None,
    exposure: str | None,
    year: int | None,
    authors: str | None,
    journal: str | None,
) -> Publication:
    license_status = {
        LicenseStatus.ALLOWED: "approved_oa_candidate",
        LicenseStatus.NEEDS_REVIEW: "needs_review",
        LicenseStatus.BLOCKED: "blocked",
    }[classification_status]
    existing = session.get(Publication, publication_id)
    if existing is None:
        existing = Publication(
            publication_id=publication_id,
            title=title,
            source_url=source_url,
            license_status=license_status,
            corpus_topic=LOCAL_EXTRAS_TOPIC,
            ingestion_status=IngestionStatus.NOT_INGESTED.value,
            doi=doi,
            year=year,
            journal=journal,
            authors=authors,
            license=license_id,
            pdf_path=pdf_path,
            pdf_url=pdf_url,
            fulltext_url=source_url,
            organism_model=organism_model,
            exposure=exposure,
            selection_notes="Registered as local extras; pending owner review.",
            human_approval="pending",
        )
        session.add(existing)
    else:
        existing.title = title
        existing.source_url = source_url
        existing.license_status = license_status
        existing.doi = doi
        existing.license = license_id
        if pdf_path:
            existing.pdf_path = pdf_path
        if pdf_url:
            existing.pdf_url = pdf_url
        if organism_model:
            existing.organism_model = organism_model
        if exposure:
            existing.exposure = exposure
        session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


def register_from_upload(
    session: Session,
    storage: LocalFileStorage,
    *,
    title: str,
    pdf_bytes: bytes,
    license_id: str,
    doi: str | None = None,
    organism_model: str | None = None,
    exposure: str | None = None,
) -> RegisterResult:
    """Store an uploaded PDF as a local-extra publication."""

    title = title.strip()
    if not title:
        raise RegisterError("title is required")
    declared = license_id.strip() or "unknown"
    if declared.lower() in {"unknown", "unspecified"}:
        classification_status = LicenseStatus.NEEDS_REVIEW
    else:
        classification = classify_license(declared)
        if classification.status is LicenseStatus.BLOCKED:
            raise RegisterError(
                classification.access_restriction_notes,
                status_code=403,
            )
        classification_status = classification.status
    normalized_doi = normalize_doi(doi) if doi else None
    publication_id = local_publication_id(doi=normalized_doi, title=title, extra="upload")
    pdf_path = persist_pdf(storage, publication_id, pdf_bytes)
    source_url = (
        f"https://doi.org/{normalized_doi}" if normalized_doi else f"local://{publication_id}"
    )
    publication = _upsert_publication(
        session,
        publication_id=publication_id,
        title=title,
        doi=normalized_doi,
        license_id=declared,
        classification_status=classification_status,
        source_url=source_url,
        pdf_url=None,
        pdf_path=pdf_path,
        organism_model=organism_model,
        exposure=exposure,
        year=None,
        authors=None,
        journal=None,
    )
    return _to_result(publication, pdf_stored=True)


def register_from_doi(
    session: Session,
    storage: LocalFileStorage,
    *,
    doi: str,
    organism_model: str | None = None,
    exposure: str | None = None,
    fetcher: HttpFetcher | None = None,
    download_pdf: bool = True,
) -> RegisterResult:
    """Fetch Crossref metadata and optionally an OA PDF when the license allows."""

    normalized = normalize_doi(doi)
    client = fetcher or UrllibFetcher()
    payload = client.get_json(_CROSSREF.format(doi=quote(normalized, safe="/")))
    message = payload.get("message")
    if not isinstance(message, dict):
        raise RegisterError("Crossref response missing message", status_code=502)

    title = _crossref_title(message)
    license_id = _crossref_license_id(message)
    if license_id == "unknown":
        classification_status = LicenseStatus.NEEDS_REVIEW
        can_download = False
    else:
        classification = classify_license(license_id)
        if classification.status is LicenseStatus.BLOCKED:
            raise RegisterError(
                classification.access_restriction_notes,
                status_code=403,
            )
        classification_status = classification.status
        can_download = classification.can_ingest

    pdf_url = _crossref_pdf_url(message)
    source_url = str(message.get("URL") or f"https://doi.org/{normalized}")
    publication_id = local_publication_id(doi=normalized, title=title, extra="doi")
    pdf_path: str | None = None
    if download_pdf and can_download and pdf_url:
        data, content_type = client.get_bytes(pdf_url)
        if "pdf" not in content_type.lower() and not is_pdf_bytes(data):
            raise RegisterError("DOI PDF URL did not return a PDF", status_code=403)
        pdf_path = persist_pdf(storage, publication_id, data)

    publication = _upsert_publication(
        session,
        publication_id=publication_id,
        title=title,
        doi=normalized,
        license_id=license_id,
        classification_status=classification_status,
        source_url=source_url,
        pdf_url=pdf_url,
        pdf_path=pdf_path,
        organism_model=organism_model,
        exposure=exposure,
        year=_crossref_year(message),
        authors=_crossref_authors(message),
        journal=_crossref_journal(message),
    )
    return _to_result(publication, pdf_stored=pdf_path is not None)


def index_registered_publication(
    session: Session,
    storage: LocalFileStorage,
    publication_id: str,
    *,
    embedding_provider: EmbeddingProvider | None = None,
) -> dict[str, Any]:
    """Run extract/chunk (and optional embed) for a registered extra."""

    publication = session.get(Publication, publication_id)
    if publication is None:
        raise RegisterError("publication not found", status_code=404)
    if not publication.pdf_path:
        raise RegisterError("no stored PDF to index", status_code=400)
    result = reprocess_publication(
        session,
        publication_id,
        storage=storage,
        actor="register_index",
    )
    embedded = 0
    if embedding_provider is not None and result.status is IngestionStatus.SUCCEEDED:
        index_result = index_chunk_embeddings(session, embedding_provider)
        session.commit()
        embedded = index_result.embedded_chunks + index_result.updated_chunks
    return {
        "publication_id": publication_id,
        "ingestion_status": result.status.value,
        "chunk_count": result.new_chunk_count,
        "embedded_count": embedded,
        "message": result.error_record.message if result.error_record else None,
    }


def _to_result(publication: Publication, *, pdf_stored: bool) -> RegisterResult:
    return RegisterResult(
        publication_id=publication.publication_id,
        doi=publication.doi,
        title=publication.title,
        license=publication.license or "unknown",
        license_status=publication.license_status,
        human_approval=publication.human_approval,
        corpus_topic=publication.corpus_topic,
        pdf_stored=pdf_stored,
    )


def _crossref_title(message: dict[str, Any]) -> str:
    titles = message.get("title")
    if isinstance(titles, list) and titles and isinstance(titles[0], str) and titles[0].strip():
        return titles[0].strip()
    raise RegisterError("Crossref record has no title", status_code=502)


def _crossref_license_id(message: dict[str, Any]) -> str:
    licenses = message.get("license")
    if isinstance(licenses, list):
        for item in licenses:
            if isinstance(item, dict) and isinstance(item.get("URL"), str):
                return license_id_from_url(item["URL"])
    return "unknown"


def _crossref_pdf_url(message: dict[str, Any]) -> str | None:
    links = message.get("link")
    if not isinstance(links, list):
        return None
    for item in links:
        if not isinstance(item, dict):
            continue
        content_type = str(item.get("content-type") or "").lower()
        url = item.get("URL")
        if "pdf" in content_type and isinstance(url, str) and url.startswith("http"):
            return url
    return None


def _crossref_year(message: dict[str, Any]) -> int | None:
    for key in ("published-print", "published-online", "issued"):
        block = message.get(key)
        if isinstance(block, dict):
            parts = block.get("date-parts")
            if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
                year = parts[0][0]
                if isinstance(year, int):
                    return year
    return None


def _crossref_authors(message: dict[str, Any]) -> str | None:
    authors = message.get("author")
    if not isinstance(authors, list):
        return None
    names: list[str] = []
    for item in authors:
        if not isinstance(item, dict):
            continue
        family = item.get("family")
        given = item.get("given")
        if isinstance(family, str) and family.strip():
            if isinstance(given, str) and given.strip():
                names.append(f"{family.strip()}, {given.strip()}")
            else:
                names.append(family.strip())
    return ", ".join(names) if names else None


def _crossref_journal(message: dict[str, Any]) -> str | None:
    container = message.get("container-title")
    if isinstance(container, list) and container and isinstance(container[0], str):
        return container[0]
    return None
