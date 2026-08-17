# Candidate graph relationship types

## Purpose

Propose edge types for a future space-biology evidence graph: what they
connect, how they stay tied to source passages, and how conflict and
qualification are represented. This note supports
[issue #72](https://github.com/bluefate/spacebio-evidence-engine/issues/72).

Node types are defined in [GRAPH_ENTITY_TYPES.md](GRAPH_ENTITY_TYPES.md) (#71).
Use cases are in
[KNOWLEDGE_GRAPH_USE_CASES.md](../architecture/KNOWLEDGE_GRAPH_USE_CASES.md)
(UC1–UC5).

## Scope

**Post-August MVP research.** No schema, extractors, or graph store.
Store choice remains [#73](https://github.com/bluefate/spacebio-evidence-engine/issues/73)
/ [#77](https://github.com/bluefate/spacebio-evidence-engine/issues/77).

## Design rules

1. **Every extracted relationship must name a source passage.** Required:
   `publication_id` plus `chunk_id` (and `source_span` when the edge is
   taken from text). Inventory-only seeds may omit `chunk_id` and stay
   `unverified` until a chunk exists (`pub_023` PDF-blocked is not eligible
   for text-derived edges).
2. **Do not encode causation unless the passage does.** Default qualifier is
   `associates`. Use `reports_cause` only when the authors claim a mechanism
   or causal effect in the cited span.
3. **Do not merge organism classes on an edge.** A `contradicts` link between
   a human Finding and a mouse Finding is forbidden; use `related_topic` at
   most, with an explicit `model_class` mismatch note.
4. **Conflicts are first-class, not LLM side effects.** Opposite outcome
   directions become `contradicts` only when comparability checks pass
   (below). Weaker or mixed statements use `qualifies`.
5. **Keep the catalog small** for [#74](https://github.com/bluefate/spacebio-evidence-engine/issues/74).
   Prefer attributes on `Finding` over a large edge zoo.

## Shared provenance (required on every extracted edge)

| Field | Required | Description |
| --- | --- | --- |
| `relationship_id` | yes | Stable id for the edge instance. |
| `relationship_type` | yes | One of the types below. |
| `from_entity_id` | yes | Source node. |
| `to_entity_id` | yes | Target node. |
| `publication_id` | yes | Corpus publication of the supporting span. |
| `chunk_id` | yes if from text | Chunk that justifies the edge. |
| `source_span` | yes if from text | Quote or offsets. |
| `source_url` | yes | DOI / landing page. |
| `epistemic_qualifier` | yes | `associates` \| `reports_cause` \| `hypothesizes` \| `reviews` |
| `extraction_method` | yes | `inventory_metadata` \| `human` \| `model` \| `mixed` |
| `verification_status` | yes | `unverified` until [#76](https://github.com/bluefate/spacebio-evidence-engine/issues/76) |
| `extractor_version` | yes for `model` | Prompt / schema / model id. |
| `confidence` | yes for `model` | Never hide low confidence. |
| `notes` | no | Comparability caveats, combined exposures, review-article scope. |

Answer-schema **Claim** edges (`supported_by`) must use citation IDs that
already passed retrieval citation validation. They must not point at
unpublished model knowledge.

## Relationship catalog

Direction is `from → to`.

### Evidence and citation (UC1)

| Type | From → to | Meaning |
| --- | --- | --- |
| `has_chunk` | Publication → Chunk | Persistence already exists; optional graph mirror. |
| `mentions` | Chunk → Organism, AnatomicalStructure, CellType, Exposure, Intervention, Assay, Outcome, Limitation | The span names that entity. |
| `supported_by` | Finding or Claim → Chunk | The result or generated claim is grounded in that passage. **Required** for every Finding/Claim. |
| `stated_in` | Finding → Publication | Convenience; must still have `supported_by` a chunk. |

### Experimental binding (UC2, UC4)

These hang off **Finding**, not off Publication metadata alone.

| Type | From → to | Meaning |
| --- | --- | --- |
| `studied_in` | Finding → Organism | Which organism/model the finding is about. |
| `under_condition` | Finding → Exposure | Spaceflight, HU, radiation, partial g, etc. Multiple allowed (e.g. HU **and** radiation). |
| `measured_in` | Finding → AnatomicalStructure or CellType | Tissue, muscle, or cell context. |
| `used_assay` | Finding → Assay | How the endpoint was measured. |
| `treated_with` | Finding → Intervention | Countermeasure or treatment when present. |
| `qualified_by` | Finding → Limitation | Sample size, analog vs flight, missing PDF, review-not-primary. |
| `combined_with` | Exposure → Exposure | Same-study combined stressors; still cite a Methods/Results span. |

### Conflict and qualification (UC3)

Comparability (all must hold before `contradicts`):

- Same `Outcome` family (compatible `preferred_label` / direction axis).
- Compatible `Organism.model_class` (human vs mouse is **not** compatible).
- Overlapping exposure *setting* (flight vs ground analog may `qualifies`, not `contradicts`, unless the passage itself equates them).
- Both Findings have `supported_by` chunks.

| Type | From → to | Meaning |
| --- | --- | --- |
| `contradicts` | Finding → Finding | Comparable findings, opposing `Outcome.direction` (or mutually exclusive states) **as stated in passages**. |
| `qualifies` | Finding → Finding | Same topic family but different condition, analog vs flight, dose, sex, or weaker/hedged wording. Not a contradiction. |
| `agrees_with` | Finding → Finding | Comparable findings, compatible direction. Optional; do not inflate. |

Do **not** add a `conflicts_with` type that skips comparability. Do **not**
treat a generated answer’s hedging as a graph conflict; conflicts live on
**Findings** (and optionally Claims that `supported_by` those findings).

### Lineage (UC5)

| Type | From → to | Meaning |
| --- | --- | --- |
| `related_study` | Publication → Publication | Shared organism/exposure/outcome families after extraction. **Not** a bibliography edge unless a chunk quotes the other DOI. |
| `cites_publication` | Publication → Publication | Out of first-pass catalog unless bibliography extraction is in scope later. |

## Worked examples

### `pub_004` (mouse, HU + radiation, myeloid infiltration)

| Type | From → to | Passage rule |
| --- | --- | --- |
| `supported_by` | Finding → Results chunk | Quote the infiltration result. |
| `studied_in` | Finding → Organism `mouse` | Methods or title span after ingest. |
| `under_condition` | Finding → Exposure `hindlimb unloading` | Same study. |
| `under_condition` | Finding → Exposure `radiation` | Same study; or `combined_with` between the two Exposures. |
| `measured_in` | Finding → AnatomicalStructure `skeletal muscle` | |
| `measured_in` | Finding → CellType `myeloid` | |
| `epistemic_qualifier` | on those edges | `associates` unless the cited sentence claims causation. |

### `pub_012` (exercise preconditioning vs HU atrophy)

`treated_with` Finding → Intervention `exercise preconditioning`.
`under_condition` Finding → Exposure `hindlimb suspension`.
Do not mark this Finding as `contradicts` a no-countermeasure atrophy Finding
without checking organism, duration, and outcome axis (`qualifies` is the
default when protocols differ).

### `pub_001` vs `pub_002` (human spaceflight vs mouse HU)

**Not** `contradicts`. Different `model_class`. Optional `related_study` on
Publications with `notes` that comparison is cross-species.

### Review articles (`pub_006`, `pub_007`)

Edges from review text use `epistemic_qualifier=reviews`. They must not be
mixed into `contradicts` against primary Findings without a curator flag.

## Non-goals

- Extraction implementation ([#74](https://github.com/bluefate/spacebio-evidence-engine/issues/74)).
- Accuracy metrics ([#75](https://github.com/bluefate/spacebio-evidence-engine/issues/75)).
- Human validation UI ([#76](https://github.com/bluefate/spacebio-evidence-engine/issues/76)).
- Causal graphs, gene-regulation edges, or citation-network scraping.

## Related documents

- [Candidate graph entity types](GRAPH_ENTITY_TYPES.md)
- [Knowledge graph use cases](../architecture/KNOWLEDGE_GRAPH_USE_CASES.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)

## Decision status

Research proposal. Not an architecture decision and not a commitment to store
these edges in Neo4j or PostgreSQL.
