"""Language model provider abstractions.

Concrete vendors (optional OpenAI, local) live in vendor modules and must not
be imported from the interface module.
"""

from spacebio_evidence_engine.llm.base import (
    ChatMessage,
    ChatRequest,
    GenerateRequest,
    GenerationResult,
    LanguageModelProvider,
    UsageMetadata,
)
from spacebio_evidence_engine.llm.openai import (
    DEFAULT_OPENAI_MODEL,
    OPENAI_API_KEY_ENV,
    OPENAI_MODEL_ENV,
    OpenAILanguageModelError,
    OpenAILanguageModelProvider,
)

__all__ = [
    "ChatMessage",
    "ChatRequest",
    "DEFAULT_OPENAI_MODEL",
    "GenerateRequest",
    "GenerationResult",
    "LanguageModelProvider",
    "OPENAI_API_KEY_ENV",
    "OPENAI_MODEL_ENV",
    "OpenAILanguageModelError",
    "OpenAILanguageModelProvider",
    "UsageMetadata",
]
