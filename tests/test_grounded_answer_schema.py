"""Schema validation tests for grounded answer responses (issue #57)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from spacebio_api.main import create_app
from spacebio_evidence_engine.schemas import (
    GROUNDED_ANSWER_SCHEMA_VERSION,
    AnswerWarning,
    AskRequest,
    ConflictFinding,
    EvidenceSufficiency,
    GroundedAnswerResponse,
    LimitationNote,
    PassageCitation,
)


def _sufficient_answer() -> GroundedAnswerResponse:
    return GroundedAnswerResponse(
        question="How does microgravity affect skeletal muscle?",
        answer_text="Evidence suggests atrophy under unloading [C1].",
        citations=[
            PassageCitation(
                citation_id="C1",
                chunk_id="chunk-1",
                publication_id="pub_001",
                title="Example study",
                section="Results",
                page=12,
                source_url="https://example.org/paper",
                excerpt="Muscle mass decreased after unloading.",
            )
        ],
        sufficiency=EvidenceSufficiency(
            status="sufficient",
            retrieved_chunk_count=3,
            supporting_publication_count=2,
        ),
        limitations=[
            LimitationNote(text="Rodent model only.", citation_ids=["C1"]),
        ],
        conflicts=[],
        warnings=[
            AnswerWarning(
                code="few_studies",
                message="Only two publications support this claim.",
            )
        ],
        model_name="fake-llm-v1",
    )


def test_schema_version_constant() -> None:
    assert GROUNDED_ANSWER_SCHEMA_VERSION == "1.0.0"
    payload = _sufficient_answer()
    assert payload.schema_version == "1.0.0"


def test_grounded_answer_round_trip() -> None:
    payload = _sufficient_answer()
    restored = GroundedAnswerResponse.model_validate(payload.model_dump())
    assert restored.citations[0].citation_id == "C1"
    assert restored.sufficiency.status == "sufficient"
    assert restored.limitations[0].text.startswith("Rodent")
    assert restored.warnings[0].code == "few_studies"


def test_insufficient_evidence_shape() -> None:
    payload = GroundedAnswerResponse(
        question="Unrelated question",
        answer_text="Insufficient evidence in the controlled corpus to answer.",
        citations=[],
        sufficiency=EvidenceSufficiency(
            status="insufficient",
            reason="No on-topic retrieved chunks above threshold.",
            retrieved_chunk_count=0,
            supporting_publication_count=0,
        ),
    )
    assert payload.citations == []
    assert payload.sufficiency.status == "insufficient"


def test_conflicts_and_limitations_optional_but_typed() -> None:
    payload = GroundedAnswerResponse(
        question="q",
        answer_text="Conflicting findings reported [C1][C2].",
        citations=[
            PassageCitation(citation_id="C1", chunk_id="a", publication_id="p1"),
            PassageCitation(citation_id="C2", chunk_id="b", publication_id="p2"),
        ],
        sufficiency=EvidenceSufficiency(status="marginal", reason="Conflict across studies."),
        conflicts=[
            ConflictFinding(
                summary="One study reports hypertrophy; another reports atrophy.",
                citation_ids=["C1", "C2"],
            )
        ],
        limitations=[LimitationNote(text="Small sample sizes.", citation_ids=["C1"])],
    )
    assert len(payload.conflicts) == 1
    assert payload.conflicts[0].citation_ids == ["C1", "C2"]


def test_ask_request_rejects_blank_question() -> None:
    with pytest.raises(ValidationError):
        AskRequest(question="")


def test_ask_request_defaults_top_k() -> None:
    req = AskRequest(question="What happens to muscle in space?")
    assert req.top_k == 8


def test_openapi_includes_grounded_answer_schemas() -> None:
    client = TestClient(create_app())
    schema = client.get("/openapi.json").json()
    components = schema["components"]["schemas"]
    assert "GroundedAnswerResponse" in components
    assert "AskRequest" in components
    assert "PassageCitation" in components
    assert "EvidenceSufficiency" in components
    assert "ConflictFinding" in components
    assert "LimitationNote" in components

    ask = schema["paths"]["/ask"]["post"]
    assert ask["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/AskRequest"
    )
    # 501 stub still documents the success response model for clients.
    success = ask["responses"]["200"]["content"]["application/json"]["schema"]
    assert success["$ref"].endswith("/GroundedAnswerResponse")
