# Observability

## Purpose
Define what the system should log, measure, and trace.

## Scope
MVP local observability and future production observability.

## Current status
Initial observability guidance.

## MVP observability
- API request logs.
- Structured semantic retrieval logs for each search, enabled by default with
  `SPACEBIO_RETRIEVAL_LOGGING_ENABLED=true` or unset. Records include query
  length, query SHA-256 hash, top-k, metadata filters, selected chunk IDs,
  ranks, scores, publication IDs, section/page provenance, source URLs,
  embedding model, embedding dimension, search algorithm, and score kind.
- Retrieval logs must not include raw user query text, prompts, secrets, API
  keys, or chunk text. Use the query hash only for repeat-query correlation.
- Verbose retrieval logging is disabled unless
  `SPACEBIO_RETRIEVAL_VERBOSE_LOGS=true`; production-like configs should leave
  verbose logging off and may set `SPACEBIO_RETRIEVAL_LOGGING_ENABLED=false`
  when retrieval trace records are not permitted.
- Developer retrieval diagnostics (issue #67) are **off by default**. Enable
  both `SPACEBIO_DEV_RETRIEVAL_DIAGNOSTICS=true` (API) and
  `NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS=true` (web) to expose
  `/dev/retrieval` and `POST /dev/retrieval-diagnostics`. The payload reuses
  retrieval-log fields: query SHA-256, query length, top-k, chunk IDs, ranks,
  scores, citation IDs (`C1`…), publication/section/page, and embedding model.
  It must not include raw query text, chunk text, prompts, secrets, or API keys.
  Leave both flags unset in production-like runs so the route 404s and the
  home-page link is hidden.
- Answer generation model, prompt version, and citation IDs.
- Ingestion run summaries.
- Structured ingestion error records with publication ID, stage, sanitized message,
  timestamp, and a failed status linked to the latest error.
- Evaluation run outputs.
- Error logs with secret redaction.

## Future observability
- Distributed tracing.
- Metrics dashboards.
- Cost monitoring by model provider.
- Retrieval quality drift monitoring.
- Corpus processing quality dashboards.

## Related documents
- [RAG architecture](RAG_ARCHITECTURE.md)
- [Evaluation strategy](../rag/EVALUATION_STRATEGY.md)
- [Security architecture](SECURITY_ARCHITECTURE.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).
