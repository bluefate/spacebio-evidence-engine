# Security Architecture

## Purpose
Define security controls for development and deployment.

## Scope
Secrets, data access, user input, model providers, logs, and dependency risk.

## Current status
Initial baseline pending threat modeling.

## MVP controls
- Environment-based secret configuration.
- Server-side model provider calls.
- Parameterized SQL through ORM/query builders.
- Least-privilege database users when practical.
- Dependency scanning in GitHub Actions.
- No restricted publications in the controlled corpus.
- Redacted logs for prompts and provider responses.

## Future controls
- Authentication and authorization.
- Role-based corpus curation.
- Audit trails for scientific metadata edits.
- Production secret manager.

## Related documents
- [Security policy](../../SECURITY.md)
- [Deployment architecture](DEPLOYMENT_ARCHITECTURE.md)
- [Observability](OBSERVABILITY.md)

## Human decisions still required
- Decide whether user accounts are MVP scope.
- Choose production secret manager.
- Approve log retention policy.

