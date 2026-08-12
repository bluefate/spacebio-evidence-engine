# Observability

## Purpose
Define what the system should log, measure, and trace.

## Scope
MVP local observability and future production observability.

## Current status
Initial observability guidance.

## MVP observability
- API request logs.
- Retrieval inputs and ranked chunk IDs.
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
