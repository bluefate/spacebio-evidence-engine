# Knowledge graph use cases

## Purpose

Identify concrete, user-facing scenarios where a knowledge graph would improve how the Space Biology Evidence Engine connects, compares, and explains evidence from the controlled corpus.

## Scope

This document is **post-August MVP** exploratory use cases. A graph database
is **not** in the product (ADR-011 / #77). Store comparison:
[GRAPH_STORE_COMPARISON.md](GRAPH_STORE_COMPARISON.md) (ADR-010).

## Use cases

### UC1: Trace a claim back to source passages and related studies

- **Actor:** Researcher reviewing an answer.
- **Trigger:** The user clicks a citation marker in a grounded answer.
- **Expected behavior:** The system shows the passage, its publication, and other passages that mention the same entities.
- **Graph value:** A graph links `Claim → Passage → Publication → Entity`, making it easy to traverse from a synthesized statement to the original evidence and to semantically related studies.

### UC2: Compare findings for the same entity across studies

- **Actor:** Researcher looking for consensus or disagreement.
- **Trigger:** The user selects an entity (for example *soleus muscle*, *microgravity*, *mouse*) from an evidence panel.
- **Expected behavior:** The system lists all passages that mention the entity, grouped by publication, experimental condition, and reported outcome.
- **Graph value:** Entity nodes (`Organism`, `Tissue`, `Exposure`, `Outcome`) connect directly to passages, enabling fast cross-study comparison without relying on vector search alone.

### UC3: Surface conflicting or contradictory findings

- **Actor:** Scientist evaluating the strength of a conclusion.
- **Trigger:** The user asks a question where studies report opposite effects.
- **Expected behavior:** The system highlights passages that share entities but report different outcomes, and explains the experimental conditions that may explain the difference.
- **Graph value:** Relationship edges (`supports`, `contradicts`, `under_condition`) between claims or passages make conflicts explicit instead of depending on the LLM to detect them during generation.

### UC4: Identify research gaps in the corpus

- **Actor:** Curator or researcher planning new work.
- **Trigger:** The user asks "What is not covered by the corpus for X?"
- **Expected behavior:** The system reports entities or relationships that are known in the literature but underrepresented in the approved publications.
- **Graph value:** A graph of `Entity → Study → Finding` makes missing combinations visible (for example, no plant studies, no human LEO data, no proteomics on X).

### UC5: Explore publication influence and evidence lineage

- **Actor:** Researcher building a literature review.
- **Trigger:** The user opens a publication detail page.
- **Expected behavior:** The system shows related publications that study similar entities, cite overlapping passages, or build on the same methods.
- **Graph value:** `Publication → Publication` edges (based on shared entities, methods, or direct citation) surface context that a plain full-text search can miss.

## Out of scope for these use cases

- Real-time graph queries in the August MVP.
- Automated entity extraction from PDFs.
- Committing to Neo4j versus PostgreSQL graph extensions — comparison in
  [GRAPH_STORE_COMPARISON.md](GRAPH_STORE_COMPARISON.md) (ADR-010). Product
  go/no-go: **no graph database** (ADR-011 / #77).

Extractor (#74), eval (#75), and human validation (#76) remain research
artifacts and are not answer-path features.

## Success criteria for future graph work

A knowledge graph should be added only if at least one of the following becomes true:

- Vector search cannot reliably satisfy UC1–UC5.
- The corpus grows large enough that manual synthesis becomes impractical.
- Maintaining explicit `Claim → Passage → Entity` edges is cheaper than repeated LLM retrieval and summarization.

## Related documents

- [Product requirements](../product/PRODUCT_REQUIREMENTS.md) — lists knowledge graph as post-August MVP.
- [Traceability matrix](../governance/TRACEABILITY_MATRIX.md) — tracks deferred knowledge graph work.
- [Candidate graph entity types](../data/GRAPH_ENTITY_TYPES.md) — node catalog and provenance (#71).
- [Candidate graph relationship types](../data/GRAPH_RELATIONSHIP_TYPES.md) — edges, passage linkage, and conflict/qualification (#72).
- [Graph store comparison](GRAPH_STORE_COMPARISON.md) — Neo4j vs PostgreSQL (#73); product go/no-go ADR-011 (#77).
- [Backlog](../governance/BACKLOG.md) — #70–#77 are **closed** (research + no graph DB).
