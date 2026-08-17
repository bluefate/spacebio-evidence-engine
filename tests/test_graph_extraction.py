from __future__ import annotations

from pathlib import Path

from spacebio_evidence_engine.graph import (
    PRODUCTION_WARNING,
    extract_from_passages,
    load_passages,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "graph_extraction_passages.json"


def test_prototype_runs_on_fixture_passages() -> None:
    passages = load_passages(FIXTURE)
    result = extract_from_passages(passages)

    assert result.experimental is True
    assert result.warning == PRODUCTION_WARNING
    assert passages
    assert any(entity.chunk_id == "chk_mouse_hu_atrophy" for entity in result.entities)


def test_outputs_include_source_chunk_ids() -> None:
    result = extract_from_passages(load_passages(FIXTURE))

    assert result.entities
    assert all(entity.chunk_id for entity in result.entities)
    assert all(rel.chunk_id for rel in result.relationships)
    assert all(entity.verification_status == "unverified" for entity in result.entities)


def test_mouse_and_human_findings_are_not_merged() -> None:
    result = extract_from_passages(load_passages(FIXTURE))
    organisms = [entity for entity in result.entities if entity.entity_type == "Organism"]
    labels = {entity.preferred_label for entity in organisms}
    assert "mouse" in labels
    assert "human" in labels
    mouse_ids = {entity.entity_id for entity in organisms if entity.preferred_label == "mouse"}
    human_ids = {entity.entity_id for entity in organisms if entity.preferred_label == "human"}
    assert mouse_ids.isdisjoint(human_ids)
    assert not any(rel.relationship_type == "contradicts" for rel in result.relationships)


def test_finding_is_supported_by_chunk() -> None:
    result = extract_from_passages(load_passages(FIXTURE))
    findings = [entity for entity in result.entities if entity.entity_type == "Finding"]
    assert findings
    finding_ids = {entity.entity_id for entity in findings}
    supported = [
        rel
        for rel in result.relationships
        if rel.relationship_type == "supported_by" and rel.from_entity_id in finding_ids
    ]
    assert supported
    assert all(rel.epistemic_qualifier == "associates" for rel in supported)


def test_unrelated_passage_emits_no_entities() -> None:
    result = extract_from_passages(load_passages(FIXTURE))
    leftover = [entity for entity in result.entities if entity.chunk_id == "chk_no_match"]
    assert leftover == []
