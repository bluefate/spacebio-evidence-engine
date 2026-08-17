"""Experimental knowledge-graph helpers (issue #74). Not used by /ask."""

from spacebio_evidence_engine.graph.extract import (
    EXTRACTOR_VERSION,
    PRODUCTION_WARNING,
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionResult,
    PassageInput,
    extract_from_passages,
    load_passages,
)

__all__ = [
    "EXTRACTOR_VERSION",
    "PRODUCTION_WARNING",
    "ExtractionResult",
    "ExtractedEntity",
    "ExtractedRelationship",
    "PassageInput",
    "extract_from_passages",
    "load_passages",
]
