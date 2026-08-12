# Security Architecture

## Purpose
Define security controls for development and deployment.

## Scope
Secrets, data access, user input, model providers, logs, and dependency risk.

## Current status
Initial baseline for local August MVP; full threat modeling before any public deployment.

## MVP controls
- Environment-based secret configuration.
- Anonymous local use (authentication out of August MVP scope).
- Server-side model provider calls.
- Optional OpenAI embeddings disabled unless `OPENAI_API_KEY` is set; API keys
  must stay in environment/local secret storage and must not be logged.
- Parameterized SQL through ORM/query builders.
- Least-privilege database users when practical.
- Dependency scanning in GitHub Actions.
- No restricted publications in the controlled corpus.
- Redacted logs for prompts and provider responses.
- Semantic retrieval logs record only structured metadata: query hash/length,
  top-k, filters, selected chunk IDs, ranks, scores, provenance fields, and
  embedding/search model lineage. Raw user queries, secrets, API keys, prompts,
  provider responses, and chunk text must not be logged.
- Production-like deployments should leave `SPACEBIO_RETRIEVAL_VERBOSE_LOGS`
  disabled and may disable structured retrieval trace logs with
  `SPACEBIO_RETRIEVAL_LOGGING_ENABLED=false` if logs are not permitted.

## Future controls
- Authentication and authorization.
- Role-based corpus curation.
- Audit trails for scientific metadata edits.
- Production secret manager.

## Related documents
- [Security policy](../../SECURITY.md)
- [Deployment architecture](DEPLOYMENT_ARCHITECTURE.md)
- [Observability](OBSERVABILITY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).
