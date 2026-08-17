"""API tests for GET /search (issue #167)."""

from __future__ import annotations

from collections.abc import Sequence

from fastapi.testclient import TestClient

from spacebio_api.config import Settings
from spacebio_api.main import create_app
from spacebio_evidence_engine.retrieval import SemanticSearchHit


class FakePassageRetriever:
    def __init__(self, hits: Sequence[SemanticSearchHit]) -> None:
        self.hits = tuple(hits)

    def __call__(self, query: str, *, top_k: int = 8) -> Sequence[SemanticSearchHit]:
        return self.hits[:top_k]


def _hit(chunk_id: str, publication_id: str) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=0.91,
        publication_id=publication_id,
        title=f"Publication {publication_id}",
        section="results",
        chunk_text="Skeletal muscle measurements changed after microgravity exposure.",
        source_url=f"https://doi.org/10.0/{publication_id}",
        page_start=5,
        page_end=5,
        section_heading="Results",
        model_name="fixture-embedding",
    )


def test_search_inventory_only_when_retriever_returns_nothing() -> None:
    app = create_app(
        Settings(APP_ENV="test"),
        passage_retriever=FakePassageRetriever([]),
    )
    client = TestClient(app)
    response = client.get("/search", params={"q": "microgravity"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "inventory_only"
    assert payload["passages"] == []


def test_search_returns_indexed_passages() -> None:
    app = create_app(
        Settings(APP_ENV="test"),
        passage_retriever=FakePassageRetriever([_hit("chunk-1", "pub_001")]),
    )
    client = TestClient(app)
    response = client.get("/search", params={"q": "microgravity", "limit": 8})
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "indexed"
    assert payload["passages"][0]["chunk_id"] == "chunk-1"
    assert payload["passages"][0]["publication_id"] == "pub_001"
    assert payload["passages"][0]["title"] == "Publication pub_001"
    assert payload["passages"][0]["section"] == "results"
    assert payload["passages"][0]["page_start"] == 5
    assert payload["passages"][0]["source_url"] == "https://doi.org/10.0/pub_001"
    assert payload["passages"][0]["excerpt"]
