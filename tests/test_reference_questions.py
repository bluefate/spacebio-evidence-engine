"""Checks for August MVP reference research questions (issue #26)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals" / "fixtures" / "reference_questions.json"
MANIFEST = ROOT / "data" / "inventory" / "august_mvp_corpus_manifest.csv"
ALLOWED_STYLES = frozenset({"factual_lookup", "comparison", "sufficiency"})


def _load() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _manifest_ids() -> set[str]:
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    header = lines[0].split(",")
    id_idx = header.index("publication_id")
    return {row.split(",")[id_idx] for row in lines[1:] if row.strip()}


def test_exactly_ten_reference_questions() -> None:
    data = _load()
    questions = data["questions"]
    assert len(questions) == 10
    assert data["topic"] == "microgravity_skeletal_muscle"
    assert data["human_scientific_review"] in {"pending", "approved"}


def test_styles_cover_lookup_comparison_and_sufficiency() -> None:
    data = _load()
    styles = {q["style"] for q in data["questions"]}
    assert styles == ALLOWED_STYLES
    assert all(q["style"] in ALLOWED_STYLES for q in data["questions"])


def test_each_question_has_evidence_characteristics() -> None:
    data = _load()
    for question in data["questions"]:
        evidence = question["expected_evidence"]
        assert isinstance(question["question"], str) and question["question"].strip()
        assert "should_be_answerable" in evidence
        assert "candidate_publication_ids" in evidence
        assert "notes" in evidence and evidence["notes"].strip()
        assert "organism_models" in evidence
        assert "exposures" in evidence
        assert "evidence_types" in evidence


def test_candidate_publications_exist_in_corpus_manifest() -> None:
    known = _manifest_ids()
    data = _load()
    for question in data["questions"]:
        for pub_id in question["expected_evidence"]["candidate_publication_ids"]:
            assert pub_id in known, f"{question['id']} unknown publication {pub_id}"


def test_sufficiency_questions_are_not_corpus_answerable() -> None:
    data = _load()
    sufficiency = [q for q in data["questions"] if q["style"] == "sufficiency"]
    assert len(sufficiency) >= 2
    for question in sufficiency:
        evidence = question["expected_evidence"]
        assert evidence["should_be_answerable"] is False
        assert evidence["candidate_publication_ids"] == []


def test_answerable_questions_list_at_least_one_candidate() -> None:
    data = _load()
    for question in data["questions"]:
        evidence = question["expected_evidence"]
        if evidence["should_be_answerable"]:
            assert evidence["candidate_publication_ids"], question["id"]


def test_questions_are_corpus_grounded_in_principle() -> None:
    """Checklist: answerable items point at corpus pubs; sufficiency items do not.

    This does not prove passage-level answerability (ingest pending). It asserts
    the fixture contracts that eval harnesses will later enforce.
    """
    data = _load()
    known = _manifest_ids()
    for question in data["questions"]:
        evidence = question["expected_evidence"]
        if evidence["should_be_answerable"]:
            assert set(evidence["candidate_publication_ids"]).issubset(known)
        else:
            assert not evidence["candidate_publication_ids"]
            assert (
                "insufficient" in evidence["notes"].lower()
                or "off-topic" in evidence["notes"].lower()
                or "out of corpus" in evidence["notes"].lower()
            )
