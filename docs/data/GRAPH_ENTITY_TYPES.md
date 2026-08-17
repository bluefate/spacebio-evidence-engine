# Candidate graph entity types

## Purpose

Propose entity types for a future space-biology evidence graph, including
definitions, required provenance, and examples mapped from the August MVP
corpus. This note supports [issue #71](https://github.com/bluefate/spacebio-evidence-engine/issues/71).

## Scope

**Post-August MVP research.** No production graph store. An experimental
gazetteer extractor exists for issue #74
([GRAPH_EXTRACTION_PROTOTYPE.md](GRAPH_EXTRACTION_PROTOTYPE.md)); it is not
wired to `/ask`.

Relationship types are specified in [GRAPH_RELATIONSHIP_TYPES.md](GRAPH_RELATIONSHIP_TYPES.md)
([#72](https://github.com/bluefate/spacebio-evidence-engine/issues/72)).

Use cases that motivate these types are in
[KNOWLEDGE_GRAPH_USE_CASES.md](../architecture/KNOWLEDGE_GRAPH_USE_CASES.md)
(UC1–UC5).

## Design rules

1. **Evidence nodes stay first-class.** Publication, passage, and chunk already
   exist in PostgreSQL. Graph entities must point at those IDs; they must not
   replace citation-first RAG.
2. **Do not merge organism classes.** Human, rodent, engineered tissue, cell
   culture, and mixed-species rows stay distinct types or distinct instances
   with an explicit `model_class` (see AGENTS.md scientific integrity).
3. **Inventory fields are coarse, not graph nodes.**
   `publications.organism_model` and `publications.exposure` are free-text
   publication labels. Graph `Organism` / `Exposure` instances are finer and
   must cite a passage, not only the inventory CSV.
4. **Extracted entities are unverified** until a human or a documented
   validation workflow ([#76](https://github.com/bluefate/spacebio-evidence-engine/issues/76))
   marks them verified.
5. **Keep the type list small.** Prefer a few types with attributes over a
   large uncontrolled ontology for the first extraction prototype ([#74](https://github.com/bluefate/spacebio-evidence-engine/issues/74)).

## Shared provenance (required on every extracted entity)

Every candidate entity instance (not the type definition) must carry:

| Field | Required | Description |
| --- | --- | --- |
| `entity_id` | yes | Stable id for the instance (not the type). |
| `entity_type` | yes | One of the types in the catalog below. |
| `preferred_label` | yes | Display name as used in the source (e.g. `soleus`). |
| `normalized_label` | no | Optional controlled term; omit rather than guess. |
| `publication_id` | yes | Corpus id (`pub_001`, …). |
| `chunk_id` | yes if extracted from text | Retrieval chunk that supports the mention. |
| `section` | when stored on the chunk | e.g. Results, Methods. |
| `page` | when stored on the chunk | Page number from ingest. |
| `source_span` | yes if extracted from text | Quoted mention or offsets into `chunk_text`. |
| `source_url` | yes | Publication `source_url` / DOI landing page. |
| `extraction_method` | yes | `inventory_metadata` \| `human` \| `model` \| `mixed`. |
| `verification_status` | yes | `unverified` until validation ([#76](https://github.com/bluefate/spacebio-evidence-engine/issues/76)). |
| `extractor_version` | yes for `model` | Model id / prompt / schema version. |
| `confidence` | yes for `model` | Numeric or ordinal; never hide low confidence. |
| `notes` | no | Ambiguity, species mix, or “review article” caveats. |

Publication-level seeds copied from the inventory (`organism_model`,
`exposure`) use `extraction_method=inventory_metadata`, may omit `chunk_id` /
`source_span`, and remain **unverified as graph nodes** until a passage
confirms them.

## Entity type catalog

| Type | Definition | Type-specific fields | Typical use case |
| --- | --- | --- | --- |
| **Publication** | An approved corpus article. Already persisted. | Existing `publications` columns | UC5 lineage |
| **Passage** / **Chunk** | Citation-addressable text unit. Already persisted as `chunks`. | Existing chunk provenance | UC1 citation walk |
| **Organism** | Living system under study. One instance per distinct organism **in a study context**; do not collapse human and mouse into one node. | `model_class`: `human` \| `mouse` \| `rat` \| `rodent_unspecified` \| `engineered_tissue` \| `cell_line` \| `multi_species` \| `other`; optional `strain`, `sex`, `life_stage` | UC2, UC4 |
| **AnatomicalStructure** | Organ, tissue, or named muscle (soleus, skeletal muscle, bone). | `structure_kind`: `organ` \| `tissue` \| `muscle` \| `other` | UC2 |
| **CellType** | Named cell population or line (myeloid, C2C12, hBMSC). | `in_vitro`: boolean when known | UC2 |
| **Exposure** | Environmental or unloading condition (ISS spaceflight, hindlimb unloading, radiation, partial g). | `setting`: `spaceflight` \| `ground_analog` \| `in_vitro_simulation` \| `review_mixed`; optional `duration`, `dose` | UC2, UC3 |
| **Intervention** | Countermeasure or treatment (exercise preconditioning, LIPUS, resveratrol, extracellular vesicles). | `intervention_kind`: `exercise` \| `pharmacologic` \| `physical` \| `cell_therapy` \| `other` | UC2, UC3 |
| **Assay** | How the outcome was measured (proteomics, telomere length, contractile function, transcriptomics). | `assay_kind` free-text until a controlled list exists | UC2 |
| **Outcome** | Reported endpoint direction or state (atrophy, infiltration, DNA damage) **as claimed in a passage**, not a global truth. | `direction` when stated: `increase` \| `decrease` \| `no_change` \| `mixed` \| `unspecified` | UC2, UC3 |
| **Finding** | A sourced result statement that binds organism + exposure + (optional) intervention + outcome. | Must cite at least one `chunk_id`; must not upgrade correlation to causation | UC1, UC3 |
| **Limitation** | Author- or curator-stated limit (n=2 astronauts, review not primary, PDF missing). | `limitation_kind` | UC3, UC4 |
| **Claim** | Generated answer claim with `citation_ids`. Exists in the answer schema today; a graph node is optional later. | Link to `Finding` / `Passage` only; never to unverified model knowledge | UC1 |

Out of catalog for the first pass (follow-ups, not #71): genes/proteins as
first-class types, missions as nodes, authors, journals, and full MeSH. Those
can be attributes on `Finding` or `Assay` until extraction quality is proven.

## Mapping from August MVP inventory

Inventory values seed **Organism** and **Exposure** candidates. They are too
coarse to be the only graph identity (e.g. `multi`, `human_evs_mouse_hu`).

| `publication_id` | Inventory `organism_model` | Inventory `exposure` | Candidate graph instances (illustrative) |
| --- | --- | --- | --- |
| `pub_001` | `human` | `spaceflight` | Organism `human` (`model_class=human`); Exposure `ISS spaceflight`; AnatomicalStructure `skeletal muscle`; Assay `proteomics`; Limitation `n=2 astronauts` (from title/notes; confirm in passage) |
| `pub_002` | `mouse` | `simulated_microgravity` | Organism `mouse`; Exposure `hindlimb unloading` (title); Assay `transcriptomics` |
| `pub_003` | `engineered_tissue` | `simulated_microgravity` | Organism/model `3D engineered skeletal muscle` (`model_class=engineered_tissue`); Outcome `attenuated myogenesis / contractile function` |
| `pub_004` | `mouse` | `hindlimb_unloading_radiation` | Organism `mouse`; two Exposures or one combined `HU + radiation`; CellType `myeloid`; AnatomicalStructure `skeletal muscle`; Outcome `infiltration` |
| `pub_009` | `rat` | `hindlimb_suspension` | Organism `rat`; AnatomicalStructure `soleus`; Exposure `7-day hindlimb suspension` |
| `pub_012` | `mouse` | `hindlimb_suspension` | Organism `mouse`; Intervention `exercise preconditioning`; Outcome `diminished atrophy` |
| `pub_016` | `engineered_human_muscle` | `spaceflight_iss` | Organism `tissue-engineered skeletal muscle` (`model_class=engineered_tissue`); Exposure `ISS`; Assay `culture hardware / experimental design` (methods-heavy) |
| `pub_018` | `human_evs_mouse_hu` | `hindlimb_unloading` | **Two Organism instances** required: human (EV donor) and mouse (HU recipient). Do not store as a single `human_evs_mouse_hu` node. Intervention `plasma extracellular vesicles`. |
| `pub_023` | `mouse` | `hindlimb_unloading` | Organism `mouse`; AnatomicalStructure `liver`, `skeletal muscle`; Outcome `dysregulated iron homeostasis`; Limitation `pdf_quality_blocked` so **no chunk provenance** until re-ingest |

Review articles (`pub_006`, `pub_007`, `organism_model=multi`) should use
`model_class=multi_species` on Organism only when the passage is mixed; prefer
per-passage organisms when the text names a species.

## Worked example (`pub_004`)

Inventory: mouse, combined hindlimb unloading and radiation, myeloid
infiltration in skeletal muscle.

| Entity type | `preferred_label` | Provenance notes |
| --- | --- | --- |
| Publication | `pub_004` | Inventory + `publications` row |
| Organism | mouse | `extraction_method=inventory_metadata` until a Methods chunk is linked |
| Exposure | hindlimb unloading | Confirm in passage; do not split from radiation unless the text does |
| Exposure | radiation | Same study context as HU |
| AnatomicalStructure | skeletal muscle | Title; attach `chunk_id` after ingest |
| CellType | myeloid | Title |
| Outcome | infiltration | Title; `direction=increase` only if the passage states increase |
| Finding | Combined HU + radiation associated with myeloid infiltration in mouse skeletal muscle | Must quote a Results span; label as association unless the paper claims causation |
| Limitation | Short format / confirm sample size in text | Unverified until chunk exists |

## Non-goals

- Implementing [#74](https://github.com/bluefate/spacebio-evidence-engine/issues/74) extraction.
- Storing entities in Alembic migrations.
- Treating inventory `organism_model` as a controlled ontology.
- Merging `pub_001` (astronaut) findings with `pub_002` (mouse) under one
  Organism node.

## Related documents

- [Knowledge graph use cases](../architecture/KNOWLEDGE_GRAPH_USE_CASES.md)
- [Candidate graph relationship types](GRAPH_RELATIONSHIP_TYPES.md)
- [Graph extraction prototype](GRAPH_EXTRACTION_PROTOTYPE.md)
- [Data dictionary](DATA_DICTIONARY.md)
- [Metadata schema](METADATA_SCHEMA.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)
- [Corpus inventory](CORPUS_INVENTORY.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)

## Decision status

Research proposal for post-August graph work. Not an architecture decision.
[#77](https://github.com/bluefate/spacebio-evidence-engine/issues/77) remains
the human go/no-go for a graph database.
