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
Until a public process is approved, report vulnerabilities privately to the repository maintainers.

## Related documents
- [Security architecture](docs/architecture/SECURITY_ARCHITECTURE.md)
- [Deployment](docs/operations/DEPLOYMENT.md)
- [Backup and recovery](docs/operations/BACKUP_AND_RECOVERY.md)

## Human decisions still required
- Choose vulnerability disclosure channel.
- Choose production identity and access model.
- Decide whether public user accounts are in scope.

