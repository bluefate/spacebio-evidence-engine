"""HTTP routes to register local-extra publications (issue #165)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from spacebio_api.config import Settings
from spacebio_evidence_engine.ingestion.register import (
    HttpFetcher,
    RegisterError,
    RegisterResult,
    index_registered_publication,
    register_from_doi,
    register_from_upload,
)
from spacebio_evidence_engine.storage.local import LocalFileStorage

router = APIRouter(prefix="/publications", tags=["publications"])
_PDF_UPLOAD = File(...)


class DoiRegisterRequest(BaseModel):
    doi: str
    organism_model: str | None = None
    exposure: str | None = None
    download_pdf: bool = True


class RegisterResponse(BaseModel):
    publication_id: str
    doi: str | None
    title: str
    license: str
    license_status: str
    human_approval: str
    corpus_topic: str
    pdf_stored: bool
    collection: str
    organism_model: str | None = None
    exposure: str | None = None


def _storage(request: Request) -> LocalFileStorage:
    stored = getattr(request.app.state, "pdf_storage", None)
    if isinstance(stored, LocalFileStorage):
        return stored
    settings: Settings = request.app.state.settings
    root = Path(settings.pdf_storage_local_root)
    if not root.is_absolute():
        root = Path.cwd() / root
    return LocalFileStorage(root)


def _session(request: Request) -> Session:
    factory: Callable[[], Session] | None = getattr(
        request.app.state, "register_session_factory", None
    )
    if factory is None:
        from spacebio_api.services import build_session_factory

        settings: Settings = request.app.state.settings
        factory = build_session_factory(settings.database_url)
        request.app.state.register_session_factory = factory
    return factory()


def _fetcher(request: Request) -> HttpFetcher | None:
    return getattr(request.app.state, "http_fetcher", None)


def _to_response(
    result: RegisterResult, *, organism: str | None, exposure: str | None
) -> RegisterResponse:
    return RegisterResponse(
        publication_id=result.publication_id,
        doi=result.doi,
        title=result.title,
        license=result.license,
        license_status=result.license_status,
        human_approval=result.human_approval,
        corpus_topic=result.corpus_topic,
        pdf_stored=result.pdf_stored,
        collection=result.collection,
        organism_model=organism,
        exposure=exposure,
    )


@router.post("/from-doi", response_model=RegisterResponse)
def from_doi(body: DoiRegisterRequest, request: Request) -> RegisterResponse:
    session = _session(request)
    try:
        result = register_from_doi(
            session,
            _storage(request),
            doi=body.doi,
            organism_model=body.organism_model,
            exposure=body.exposure,
            fetcher=_fetcher(request),
            download_pdf=body.download_pdf,
        )
    except RegisterError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        session.close()
    return _to_response(result, organism=body.organism_model, exposure=body.exposure)


@router.post("/from-pdf", response_model=RegisterResponse)
async def from_pdf(
    request: Request,
    title: str = Form(...),
    license_id: str = Form("unknown"),
    doi: str | None = Form(None),
    organism_model: str | None = Form(None),
    exposure: str | None = Form(None),
    file: UploadFile = _PDF_UPLOAD,
) -> RegisterResponse:
    data = await file.read()
    session = _session(request)
    try:
        result = register_from_upload(
            session,
            _storage(request),
            title=title,
            pdf_bytes=data,
            license_id=license_id,
            doi=doi,
            organism_model=organism_model,
            exposure=exposure,
        )
    except RegisterError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        session.close()
    return _to_response(result, organism=organism_model, exposure=exposure)


def _pdf_root(request: Request) -> Path:
    settings: Settings = request.app.state.settings
    root = Path(settings.pdf_storage_local_root)
    if not root.is_absolute():
        root = Path.cwd() / root
    return root


@router.get("/catalog-pdfs/status")
def catalog_pdf_status(request: Request) -> dict[str, Any]:
    from spacebio_evidence_engine.corpus.fetch import corpus_pdf_disk_status

    return corpus_pdf_disk_status(_pdf_root(request))


@router.post("/catalog-pdfs/fetch-missing")
def fetch_missing_catalog_pdfs(request: Request) -> dict[str, Any]:
    from spacebio_evidence_engine.corpus.fetch import fetch_corpus_pdfs

    results = fetch_corpus_pdfs(_pdf_root(request), force=False)
    downloaded = [item.publication_id for item in results if item.outcome == "downloaded"]
    skipped = [item.publication_id for item in results if item.outcome.startswith("skipped_")]
    failed = [
        {"publication_id": item.publication_id, "message": item.message}
        for item in results
        if item.outcome.startswith("failed_")
    ]
    return {
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
        "downloaded_count": len(downloaded),
        "failed_count": len(failed),
        "message": (
            f"Downloaded {len(downloaded)} PDF(s). "
            "This does not index or train. Run make ingest (or Index per paper) next."
        ),
    }


@router.post("/{publication_id}/index")
def index_publication(publication_id: str, request: Request) -> dict[str, Any]:
    session = _session(request)
    try:
        return index_registered_publication(session, _storage(request), publication_id)
    except RegisterError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        session.close()
