# Human validation workflow for extracted graph claims

## Purpose

Define how extracted graph claims move from machine output to human-approved
graph facts without allowing unverified extractions to silently enter product
answers.

## Scope

This workflow applies to post-August knowledge-graph research and any future
extraction prototype that produces candidate entities, relationships, or claims
from passages in the controlled corpus.

It does **not** authorize a graph database, extraction pipeline, or answer-time
graph reasoning. ADR-011 / #77: no graph database in the product.

## Workflow steps

1. Extraction jobs produce candidate graph claims from a specific passage.
2. Each candidate claim is stored with immutable provenance:
   - `claim_id`
   - `entity_ids` / `relationship_ids`
   - `publication_id`
   - `chunk_id`
   - `section`
   - `page`
   - `source_span`
   - `extractor_version`
   - `confidence`
   - `verification_status = unverified`
3. Unverified claims are visible to reviewers and evaluators, but they remain
   excluded from any user-facing answer path.
4. A human reviewer checks the claim against the source passage and selects one
   of the acceptance states below.
5. Only claims in an accepted state may be promoted to trusted graph facts.
6. Rejected claims remain in the audit trail with their provenance and review
   notes.

## Roles

| Role | Responsibilities |
| --- | --- |
| Extractor | Produces candidate claims and provenance; never marks a claim verified. |
| Human reviewer | Checks the claim against the source passage and decides the acceptance state. |
| Curator / maintainer | Resolves disagreements, updates workflow rules, and reviews edge cases. |
| System | Enforces that unverified claims cannot be used as answer evidence. |

## Acceptance states

| State | Meaning | Allowed next step |
| --- | --- | --- |
| `unverified` | Newly extracted or not yet reviewed. | Human review required. |
| `verified` | Reviewer confirms the claim is supported by the cited passage. | Eligible for trusted graph use. |
| `needs_revision` | Claim is plausible but needs corrected labels, provenance, or span. | Send back to extraction / curation. |
| `rejected` | Passage does not support the claim or the claim is out of scope. | Retain for audit only. |
| `deprecated` | Previously accepted but later superseded or invalidated. | Hide from trusted graph outputs. |

## Decision rules

- A claim cannot become `verified` without a passage-level citation.
- A claim cannot be promoted if its provenance is incomplete.
- If the reviewer cannot point to the exact passage span, the claim remains
  `unverified` or becomes `needs_revision`.
- If multiple reviewers disagree, the curator makes the final call and records
  the rationale.
- Answer generation may only consume claims marked `verified` or equivalent
  trusted-state entries defined by the implementation.

## Enforcement requirements

- Answer-time retrieval must filter out `unverified` claims.
- UI and API surfaces must label unverified graph data as draft or provisional.
- Evaluation jobs may inspect unverified claims, but they must not score them as
  trusted evidence.
- Any fallback that would expose unverified claims to answer generation must
  fail closed.

## Audit trail

Every review decision should record:

- reviewer identity
- review timestamp
- source passage reference
- decision state
- rationale or correction notes
- any linked follow-up issue

## Open questions

- Whether `verified` should be the only trusted state or whether a second
  curated trust tier is needed later.
- Whether the first prototype should store review events in the application
  database or in a separate moderation log.
- Whether automated sampling should surface low-confidence claims first.

## Related documents

- [Candidate graph entity types](../data/GRAPH_ENTITY_TYPES.md)
- [Candidate graph relationship types](../data/GRAPH_RELATIONSHIP_TYPES.md)
- [Knowledge graph use cases](../architecture/KNOWLEDGE_GRAPH_USE_CASES.md)
- [Traceability matrix](TRACEABILITY_MATRIX.md)
- [Backlog](BACKLOG.md)

## Decision status

Research guidance. Extraction prototype (#74) and eval (#75) exist; claims stay
`unverified` until the [validation workflow](VALIDATION_WORKFLOW.md) is applied.
**No graph database** (ADR-011 / #77). Do not send gazetteer output to `/ask`.
