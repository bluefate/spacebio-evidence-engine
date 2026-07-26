# Data Dictionary

## Purpose
Define core domain terms consistently.

## Scope
MVP data entities and evidence concepts.

## Current status
Initial dictionary.

## Terms
- Publication: A scientific article included in the controlled corpus.
- Source: The original access location, DOI, repository URL, PDF, or HTML source.
- Passage: A citation-addressable text span with page or section metadata.
- Chunk: A retrieval unit derived from one or more passages.
- Citation: A link from an answer claim to a supporting passage.
- Organism: Biological organism studied.
- Model system: Experimental model such as rodent, cell culture, tissue, or human sample.
- Exposure: Spaceflight, microgravity, simulated microgravity, radiation, unloading, or related condition.
- Measurement: Observed assay, endpoint, omics feature, or physiological result.
- Finding: A sourced statement about an observed result.
- Limitation: A sourced statement about study limits or uncertainty.
- Evidence gap: A corpus-limited area where evidence is absent, sparse, or inconsistent.
- Candidate conflict: A possible disagreement requiring human/scientific review.

## Related documents
- [Metadata schema](METADATA_SCHEMA.md)
- [Corpus specification](CORPUS_SPECIFICATION.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)

## Human decisions still required
- Approve controlled vocabularies.
- Decide whether ontology mappings are MVP scope.

