# SECURITY

## Purpose
Define initial security expectations for a research evidence engine.

## Scope
Applies to local development, application services, database access, model provider keys, user input, logs, and deployment.

## Current status
Initial baseline. A full threat model should be completed before public deployment.

## Security requirements
- Store secrets in environment variables or approved secret managers.
- Do not commit API keys, PDFs with restricted rights, private notes, or credentials.
- Treat user questions and uploaded files as untrusted input.
- Sanitize and parameterize all database access.
- Keep model provider calls behind server-side abstractions.
- Avoid logging secrets, full prompts containing sensitive values, or unnecessary user data.
- Use dependency scanning in CI.
- Require HTTPS outside local development.

## Vulnerability reporting
Report vulnerabilities via this file and GitHub security advisories to repository maintainers.

## Related documents
- [Security architecture](docs/architecture/SECURITY_ARCHITECTURE.md)
- [Deployment](docs/operations/DEPLOYMENT.md)
- [Backup and recovery](docs/operations/BACKUP_AND_RECOVERY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](docs/governance/DECISION_LOG.md).

