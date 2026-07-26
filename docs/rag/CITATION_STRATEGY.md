# Citation Strategy

## Purpose
Ensure every scientific answer can be verified against source passages.

## Scope
Passage-level citation model for MVP.

## Current status
Initial strategy.

## Requirements
- Cite at passage level, not only publication level.
- Store page, section, source URL, and text span where available.
- Link each answer claim to supporting passage IDs.
- Show cited passages in the UI.
- Omit unsupported claims.
- Warn when evidence is based on few passages or few studies.
- Preserve limitations when relevant.

## Citation validation
The system should verify that cited passage IDs were present in retrieved context before returning the answer.

## Related documents
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)
- [Metadata schema](../data/METADATA_SCHEMA.md)
- [Prompting strategy](PROMPTING_STRATEGY.md)

## Human decisions still required
- Approve citation display format.
- Define acceptable citation granularity.

