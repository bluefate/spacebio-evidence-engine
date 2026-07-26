# Backup and Recovery

## Purpose
Define how project data can be restored after loss or corruption.

## Scope
PostgreSQL data, corpus manifests, processed artifacts, prompts, and evaluation results.

## Current status
Initial policy.

## MVP approach
- Keep source docs and corpus manifest versioned where rights permit.
- Regenerate processed text, chunks, and embeddings from source artifacts.
- Back up PostgreSQL before destructive migrations.
- Store prompt versions and evaluation outputs.

## Future approach
Use managed database backups, object storage versioning, and recovery drills.

## Related documents
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)
- [Deployment](DEPLOYMENT.md)
- [Security architecture](../architecture/SECURITY_ARCHITECTURE.md)

## Human decisions still required
- Approve backup frequency.
- Decide which generated artifacts are stored versus regenerated.

