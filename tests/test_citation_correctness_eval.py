"""Tests for citation correctness evaluation (issue #59)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from spacebio_evidence_engine.evaluation.citation_correctness import (
    CitationCorrectnessMetrics,
    ClaimCitationCheck,
    RetrievedCitationEvidence,
    evaluate_case,
    evaluate_cases,
    load_cases,
)
from spacebio_evidence_engine.schemas import (
    EvidenceSufficiency,
    GroundedAnswerResponse,
    PassageCitation,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals/fixtures/citation_correctness_answers.json"
SCRIPT = ROOT / "evals/citation_correctness.py"


def _answer(
    *,
    answer_text: str = "Soleus mass decreased after unloading [C1].",
    citations: list[PassageCitation] | None = None,
) -> GroundedAnswerResponse:
    return GroundedAnswerResponse(
        question="How does microgravity affect skeletal muscle?",
        answer_text=answer_text,
        citations=citations
        if citations is not None
        else [
            PassageCitation(
                citation_id="C1",
                chunk_id="chunk_1",
                publication_id="pub_001",
                title="Microgravity skeletal muscle study",
                section="Results",
                page=4,
                source_url="https://doi.org/10.0/example",
                excerpt="Soleus mass decreased after unloading.",
            )
        ],
        sufficiency=EvidenceSufficiency(
            status="sufficient",
            retrieved_chunk_count=3,
            supporting_publication_count=2,
        ),
    )


def _retrieved() -> list[RetrievedCitationEvidence]:
    return [
        RetrievedCitationEvidence(
            citation_id="C1",
            chunk_id="chunk_1",
            publication_id="pub_001",
            title="Microgravity skeletal muscle study",
            section="Results",
            page=4,
            source_url="https://doi.org/10.0/example",
        )
    ]


def test_retrieved_citation_ids_and_claim_labels_pass() -> None:
    case = load_cases(FIXTURE)[0]

    result = evaluate_case(case)

    assert result.passed
    assert result.citation_id_precision == 1.0
    assert result.answer_marker_precision == 1.0
    assert result.claim_citation_precision == 1.0
    assert result.claim_citation_recall == 1.0


def test_emitted_citation_not_in_retrieved_context_fails() -> None:
    result = evaluate_case(
        load_cases(FIXTURE)[0].model_copy(
            update={
                "answer": _answer(
                    citations=[
                        PassageCitation(
                            citation_id="C9",
                            chunk_id="chunk_9",
                            publication_id="pub_009",
                        )
                    ],
                    answer_text="Unsupported citation is referenced [C9].",
                )
            }
        )
    )

    assert not result.passed
    assert result.citation_id_precision == 0.0
    assert "citation_id_not_retrieved" in {finding.code for finding in result.findings}


def test_answer_marker_must_match_emitted_citation() -> None:
    result = evaluate_case(
        load_cases(FIXTURE)[0].model_copy(
            update={"answer": _answer(answer_text="Soleus mass decreased [C404].")}
        )
    )

    assert not result.passed
    assert result.answer_marker_precision == 0.0
    assert "answer_marker_not_emitted" in {finding.code for finding in result.findings}


def test_claim_precision_and_recall_report_false_positive_and_negative() -> None:
    case = load_cases(FIXTURE)[0].model_copy(
        update={
            "claim_checks": [
                ClaimCitationCheck(
                    claim_id="claim_1",
                    claim_text="Soleus mass decreased.",
                    expected_citation_ids=["C1", "C2"],
                    actual_citation_ids=["C1", "C3"],
                )
            ]
        }
    )

    result = evaluate_case(case)

    assert not result.passed
    assert result.claim_citation_precision == 0.5
    assert result.claim_citation_recall == 0.5
    assert {finding.code for finding in result.findings} == {
        "claim_citation_false_positive",
        "claim_citation_false_negative",
    }


def test_fixture_cases_emit_aggregate_metrics() -> None:
    metrics, *results = evaluate_cases(load_cases(FIXTURE))

    assert isinstance(metrics, CitationCorrectnessMetrics)
    assert metrics.passed
    assert metrics.case_count == 1
    assert metrics.citation_id_precision == 1.0
    assert all(result.passed for result in results)


def test_cli_returns_nonzero_for_bad_citation_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "bad_citations.json"
    fixture.write_text(
        """
        {
          "cases": [
            {
              "case_id": "bad",
              "answer": {
                "question": "q",
                "answer_text": "Microgravity reduced muscle size [C2].",
                "citations": [
                  {"citation_id": "C2", "chunk_id": "chunk_2", "publication_id": "pub_002"}
                ],
                "sufficiency": {
                  "status": "sufficient",
                  "retrieved_chunk_count": 3,
                  "supporting_publication_count": 2
                }
              },
              "retrieved_context": [
                {"citation_id": "C1", "chunk_id": "chunk_1", "publication_id": "pub_001"}
              ]
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(fixture)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "citation_id_not_retrieved" in completed.stdout


def test_cli_returns_zero_for_checked_fixture() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURE), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert '"claim_citation_recall": 1.0' in completed.stdout
