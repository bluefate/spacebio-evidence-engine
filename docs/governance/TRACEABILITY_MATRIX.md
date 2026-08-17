# Traceability Matrix

## Purpose
Map requirements to design and verification artifacts.

## Scope
August MVP (deadline 2026-08-31) and deferred post-August items.

## Current status
Aligned with [decision log](DECISION_LOG.md) and [product requirements](../product/PRODUCT_REQUIREMENTS.md).

## August MVP matrix

| Requirement | Design document | Verification | Tracking |
| --- | --- | --- | --- |
| Natural-language search (vector) | [Retrieval strategy](../rag/RETRIEVAL_STRATEGY.md) | Retrieval smoke / draft benchmarks | [Issues](https://github.com/bluefate/spacebio-evidence-engine/issues?q=label%3Amilestone%3Aretrieval) |
| Scientific Q&A | [RAG architecture](../architecture/RAG_ARCHITECTURE.md) | Answer smoke tests | [Issues](https://github.com/bluefate/spacebio-evidence-engine/issues?q=label%3Amilestone%3Agrounded-answers) |
| Passage-level citations | [Citation strategy](../rag/CITATION_STRATEGY.md) | Citation validation tests | Same as Q&A |
| Evidence insufficiency | [Prompting strategy](../rag/PROMPTING_STRATEGY.md) | Insufficient-evidence tests | Same as Q&A |
| Corpus control (~10–15 OA) | [Corpus specification](../data/CORPUS_SPECIFICATION.md) | Manifest + license review | [Issues](https://github.com/bluefate/spacebio-evidence-engine/issues?q=label%3Amilestone%3Acorpus-discovery) |
| Minimal citation UI | [design.md](../../design.md) | Manual/smoke UI | [Issues](https://github.com/bluefate/spacebio-evidence-engine/issues?q=label%3Amilestone%3Aweb-interface) |
| Local Compose deploy | [Deployment architecture](../architecture/DEPLOYMENT_ARCHITECTURE.md) | `make services` / local demo | [Issues](https://github.com/bluefate/spacebio-evidence-engine/issues?q=label%3Amilestone%3Afoundation) |

## Deferred past August (not August MVP)

| Requirement | Notes | Tracking |
| --- | --- | --- |
| Study comparison | Shipped as inventory `/compare` (not a findings synthesizer) | [#65](https://github.com/bluefate/spacebio-evidence-engine/issues/65) |
| Hybrid / full-text / rerank retrieval | Implemented post-August; optional / off by default | [#45](https://github.com/bluefate/spacebio-evidence-engine/issues/45), [#46](https://github.com/bluefate/spacebio-evidence-engine/issues/46), [#48](https://github.com/bluefate/spacebio-evidence-engine/issues/48) |
| Entity inspection / extraction | Free-text metadata only in August | Post-August |
| Human validation of extracted graph claims | Candidate claims remain unverified until review | [Validation workflow](VALIDATION_WORKFLOW.md), [#76](https://github.com/bluefate/spacebio-evidence-engine/issues/76) |
| Knowledge graph view / Neo4j | **No** graph database (ADR-011) | [#77](https://github.com/bluefate/spacebio-evidence-engine/issues/77), [GRAPH_STORE_COMPARISON.md](../architecture/GRAPH_STORE_COMPARISON.md) |

## Project board

- **Project:** [Space Biology Evidence Engine](https://github.com/users/bluefate/projects/6)
- **Issues:** [All issues](https://github.com/bluefate/spacebio-evidence-engine/issues)
- **Backlog index:** [BACKLOG.md](BACKLOG.md)

## Related documents
- [Product requirements](../product/PRODUCT_REQUIREMENTS.md)
- [Testing strategy](../development/TESTING_STRATEGY.md)
- [Evaluation strategy](../rag/EVALUATION_STRATEGY.md)
- [Decision log](DECISION_LOG.md)
- [Build plan](../../plan.md)
