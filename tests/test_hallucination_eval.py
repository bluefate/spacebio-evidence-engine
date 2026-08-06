"""Tests for hallucination evaluation checks (issue #58)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from spacebio_evidence_engine.evaluation.hallucination import (
    HallucinationMetrics,
    evaluate_answer,
    evaluate_answers,
    load_answers,
)
from spacebio_evidence_engine.schemas import (
    EvidenceSufficiency,
    GroundedAnswerResponse,
    PassageCitation,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals/fixtures/hallucination_answers.json"
SCRIPT = ROOT / "evals/hallucination_check.py"


def _answer(answer_text: str) -> GroundedAnswerResponse:
    return GroundedAnswerResponse(
        question="How does unloading affect muscle?",
        answer_text=answer_text,
        citations=[
            PassageCitation(
                citation_id="C1",
                chunk_id="chk_1",
                publication_id="pub_001",
                excerpt="Muscle mass decreased after unloading.",
            )
        ],
        sufficiency=EvidenceSufficiency(
            status="sufficient",
            retrieved_chunk_count=3,
            supporting_publication_count=2,
        ),
    )


def test_cited_claim_passes() -> None:
    result = evaluate_answer(_answer("Unloading decreased muscle mass in the fixture [C1]."))
    assert result.passed
    assert result.claim_sentence_count == 1
    assert result.cited_claim_sentence_count == 1


def test_uncited_claim_fails_actionably() -> None:
    result = evaluate_answer(_answer("Unloading decreased muscle mass in the fixture."))
    assert not result.passed
    assert result.findings[0].code == "unsupported_claim"
    assert "Unloading decreased" in result.findings[0].text


@pytest.mark.parametrize(
    "answer_text",
    [
        "Astronauts lose soleus mass.",
        "Unloading induces muscle atrophy.",
        "Radiation impaired muscle function.",
    ],
)
def test_expanded_claim_lexicon_flags_uncited_verbs(answer_text: str) -> None:
    result = evaluate_answer(_answer(answer_text))
    assert not result.passed
    assert result.findings[0].code == "unsupported_claim"
    assert answer_text in result.findings[0].text


def test_unknown_citation_marker_fails() -> None:
    result = evaluate_answer(_answer("Unloading decreased muscle mass in the fixture [C9]."))
    assert not result.passed
    assert result.findings[0].code == "unknown_citation_marker"
    assert result.findings[0].text == "C9"


def test_insufficient_response_must_decline_without_citations() -> None:
    result = evaluate_answer(
        GroundedAnswerResponse(
            question="q",
            answer_text="Microgravity decreased muscle mass [C1].",
            citations=[PassageCitation(citation_id="C1", chunk_id="chk_1", publication_id="p1")],
            sufficiency=EvidenceSufficiency(status="insufficient"),
        )
    )
    assert not result.passed
    assert {finding.code for finding in result.findings} == {
        "insufficient_has_citations",
        "insufficient_has_markers",
        "insufficient_not_explicit",
    }


def test_fixture_answers_pass_and_emit_metrics() -> None:
    answers = load_answers(FIXTURE)
    metrics, *results = evaluate_answers(answers)
    assert isinstance(metrics, HallucinationMetrics)
    assert metrics.passed
    assert metrics.answer_count == 2
    assert metrics.unsupported_claim_count == 0
    assert all(result.passed for result in results)


def test_cli_returns_nonzero_for_unsupported_claim_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "answers.json"
    fixture.write_text(
        """
        {
          "answers": [
            {
              "question": "q",
              "answer_text": "Microgravity decreased muscle mass.",
              "citations": [
                {"citation_id": "C1", "chunk_id": "chk_1", "publication_id": "p1"}
              ],
              "sufficiency": {
                "status": "sufficient",
                "retrieved_chunk_count": 3,
                "supporting_publication_count": 2
              }
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
    assert "unsupported_claim" in completed.stdout


def test_cli_returns_zero_for_checked_fixture() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURE), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    assert '"unsupported_claim_count": 0' in completed.stdout
