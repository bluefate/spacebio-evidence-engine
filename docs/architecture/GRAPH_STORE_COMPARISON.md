# Graph store comparison: Neo4j vs PostgreSQL

## Purpose

Compare Neo4j and PostgreSQL-based graph modeling for the knowledge-graph use
cases (UC1–UC5). This is a post-August research note for
[issue #73](https://github.com/bluefate/spacebio-evidence-engine/issues/73).
It does **not** add Neo4j (or Apache AGE) as a repository dependency.

## Scope

Options in scope:

1. **PostgreSQL adjacency tables** — `entities` / `relationships` (or equivalent)
   with foreign keys to `publications` and `chunks`, queried with SQL joins and
   recursive CTEs.
2. **Neo4j** — property graph + Cypher, separate process from the RAG database.
3. **PostgreSQL graph extension (Apache AGE)** — Cypher-on-Postgres. Noted as a
   middle path; not recommended for the next increment (ops and provenance
   still need the same FK discipline as option 1).

Out of scope: implementing a graph store or wiring gazetteer output (#74) into
`/ask`. Product go/no-go is ADR-011 (#77): **no graph database**.

## Use cases under comparison

From [KNOWLEDGE_GRAPH_USE_CASES.md](KNOWLEDGE_GRAPH_USE_CASES.md):

| ID | Need | Typical access pattern |
| --- | --- | --- |
| UC1 | Claim → passage → publication → entity | 1–2 hop, always via chunk/publication ids |
| UC2 | Same entity across studies | Filter by entity type + label; group by publication and organism |
| UC3 | Conflicts | Typed `contradicts` / `qualifies` edges with comparability rules |
| UC4 | Gaps | Aggregate missing organism × exposure × assay combinations |
| UC5 | Related publications | Shared-entity or related-topic joins |

Citation-first RAG remains the product: graph rows must not replace retrieved
passages as evidence.

## Cost

| | PostgreSQL tables | Neo4j |
| --- | --- | --- |
| Incremental infra | None (Compose Postgres already required) | Second datastore: image, volume, RAM, backup |
| License / hosting | Existing Postgres (local Compose; no Aura) | Community Server is free to run locally; Aura and enterprise features add cost and vendor process |
| Engineering | Alembic + SQLAlchemy, same as chunks/embeddings | New client, migrations story, dual-write or ETL from Postgres |
| Corpus scale (23 papers) | SQL is enough for UC1–UC5 | Neo4j cost is not justified by size |

**Cost verdict:** PostgreSQL wins while the corpus is small and local-only
(ADR-002, D7). Neo4j cost is operational and cognitive, not license, at this
scale.

## Operations

| | PostgreSQL tables | Neo4j |
| --- | --- | --- |
| Local demo | One database URL | Second health check, credentials, and failure mode (`/ask` must still work if graph is down) |
| Backups | Existing volume / dump story | Separate dump (`neo4j-admin`) or lose graph independently of citations |
| Consistency | FK to `publications` / `chunks` can `ON DELETE` with reprocess (#35) | Properties can orphan when chunks are replaced unless ETL is transactional |
| Security | Same `DATABASE_URL` surface | Extra network port and auth secrets |
| Agents / CI | Already in `make migrate` | New Compose service and CI skip/flake surface |

**Ops verdict:** A second graph database increases demo fragility. The live
local path is already the highest product risk; do not add a required Neo4j
container until a curator UI or multi-hop product actually needs it.

## Query patterns

| Use case | PostgreSQL | Neo4j |
| --- | --- | --- |
| UC1 provenance walk | `JOIN chunks` / `publications` on ids already in the RAG schema | Cypher path is shorter to write; still must store the same ids |
| UC2 entity grouping | `WHERE entity_type = … GROUP BY publication_id, organism` | Label indexes; easy `MATCH (e:Organism)-->(p:Passage)` |
| UC3 conflicts | `WHERE relationship_type = 'contradicts'` plus SQL checks that organism classes differ | Cypher is natural for `contradicts`; rules still live in application code |
| UC4 gaps | `GROUP BY` / anti-joins against inventory organism × exposure | Possible; aggregation is not Neo4j’s main advantage |
| UC5 related pubs | Shared-entity self-join | Variable-length paths shine if influence hops grow beyond 2–3 |

Deep, variable-length traversal and interactive graph visualization are the
clearest Neo4j advantages. UC1–UC4 on this corpus are filter-and-join, not
open-ended path search.

**Query verdict:** Prefer SQL until a product surface needs interactive
multi-hop exploration.

## Provenance

Required on extracted edges ([GRAPH_RELATIONSHIP_TYPES.md](../data/GRAPH_RELATIONSHIP_TYPES.md)):
`publication_id`, `chunk_id` (when from text), `source_span`,
`verification_status`, `extraction_method`.

| | PostgreSQL tables | Neo4j |
| --- | --- | --- |
| Integrity | Foreign keys to real chunk rows; reprocess can cascade | Easy to store dangling chunk ids after re-ingest |
| Citation-first | Same database as passages used by `/ask` | Dual store: graph can drift from retrieved evidence |
| Unverified extraction | `verification_status` column; keep out of answers (same as #74/#76) | Same field as a property; no extra safety unless app enforces it |
| Organism classes | Check constraints / distinct `entity_type` rows | Labels can still be merged by a bad load job |

**Provenance verdict:** PostgreSQL FKs are the better default for a
citation-first engine. If Neo4j is added later, Postgres remains source of
truth and Neo4j is a derived projection.

## Recommendation (ADR-010) and product go/no-go (ADR-011)

**Modeling:** If graph rows are stored at all, use PostgreSQL adjacency tables
with `publication_id` / `chunk_id` foreign keys. Do not add Neo4j as a
dependency for modeling.

**Product (issue #77 / ADR-011):** **No graph database.** Do not add Neo4j,
Apache AGE, or another graph engine to Compose or application code. Catalogs,
the experimental extractor, eval, and the validation workflow stay research
artifacts. Grounded answers remain retrieval + citations only.

Suggested PostgreSQL shape (not implemented; not required by ADR-011):

- Tables aligned with #71/#72 catalogs, every text-derived row pointing at
  `publication_id` + `chunk_id`.
- `verification_status` default `unverified`; never feed gazetteer output into
  grounded answers.

## Related documents

- [Decision log](../governance/DECISION_LOG.md) — ADR-010, ADR-011
- [Knowledge graph use cases](KNOWLEDGE_GRAPH_USE_CASES.md)
- [Data architecture](DATA_ARCHITECTURE.md)
- [Graph extraction prototype](../data/GRAPH_EXTRACTION_PROTOTYPE.md)
