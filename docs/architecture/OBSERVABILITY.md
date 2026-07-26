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

## Human decisions still required
- Approve logging detail for prompts.
- Choose production observability stack.

