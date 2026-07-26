# Risk Register

## Purpose
Track project risks and mitigations.

## Scope
Scientific, technical, data, security, and delivery risks.

## Current status
Initial risk register.

## Risks
| ID | Risk | Impact | Mitigation |
| --- | --- | --- | --- |
| R-001 | Hallucinated scientific claims | High | Ground answers only in retrieved passages |
| R-002 | Citation mismatch | High | Validate cited passage IDs and evaluate citations |
| R-003 | Poor PDF extraction | Medium | Track extraction quality and reject poor sources |
| R-004 | Corpus bias | Medium | Disclose corpus limits |
| R-005 | False conflict detection | Medium | Label as candidate conflicts requiring review |
| R-006 | Licensing uncertainty | High | Require license review before ingestion |
| R-007 | Model provider lock-in | Medium | Use provider abstraction |
| R-008 | Scope creep | High | Keep Neo4j and advanced workflows future-phase |

## Related documents
- [Product requirements](../product/PRODUCT_REQUIREMENTS.md)
- [Evaluation strategy](../rag/EVALUATION_STRATEGY.md)
- [Security architecture](../architecture/SECURITY_ARCHITECTURE.md)

## Human decisions still required
- Assign owners.
- Approve risk severity scale.

