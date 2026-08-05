"""Language model provider interface (issue #51).

Provider-agnostic types and ABC only. Do not import OpenAI, Anthropic,
or other vendor SDKs in this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

ChatRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class ChatMessage:
    """One turn in a chat-style generation request."""

    role: ChatRole
    content: str


@dataclass(frozen=True, slots=True)
class UsageMetadata:
    """Optional token/usage accounting when the backend reports it."""

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    # Provider-specific extras (cost estimates, cached tokens, etc.)
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Model output plus optional usage metadata."""

    text: str
    model_name: str
    usage: UsageMetadata | None = None
    # Parsed structured payload when structured_output was requested.
    structured: Mapping[str, Any] | None = None
    finish_reason: str | None = None


@dataclass(frozen=True, slots=True)
class GenerateRequest:
    """Single-prompt generation."""

    prompt: str
    system: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    # Optional JSON Schema (or equivalent) for structured responses.
    structured_output: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """Multi-turn chat generation."""

    messages: Sequence[ChatMessage]
    temperature: float | None = None
    max_tokens: int | None = None
    structured_output: Mapping[str, Any] | None = None


class LanguageModelProvider(ABC):
    """Swappable LLM backend for grounded answer generation.

    Concrete providers (optional OpenAI, local stubs, etc.) implement this
    ABC in follow-on issues. Call sites must depend only on this interface.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Stable model identifier recorded with generation logs."""

    @abstractmethod
    def generate(self, request: GenerateRequest) -> GenerationResult:
        """Generate a completion from a single prompt (plus optional system)."""

    @abstractmethod
    def chat(self, request: ChatRequest) -> GenerationResult:
        """Generate a completion from a chat message list."""
