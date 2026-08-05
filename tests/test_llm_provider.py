"""Unit tests for the language model provider interface (issue #51)."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from spacebio_evidence_engine.llm import (
    ChatMessage,
    ChatRequest,
    GenerateRequest,
    GenerationResult,
    LanguageModelProvider,
    UsageMetadata,
)
from spacebio_evidence_engine.llm.base import LanguageModelProvider as BaseLanguageModelProvider

ROOT = Path(__file__).resolve().parents[1]
INTERFACE_MODULE = ROOT / "src/spacebio_evidence_engine/llm/base.py"

_FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "openai",
        "anthropic",
        "httpx",
        "requests",
        "tiktoken",
        "transformers",
        "torch",
    }
)


class FakeLanguageModelProvider(LanguageModelProvider):
    """Deterministic stand-in used only in tests."""

    def __init__(self, *, model_name: str = "fake-llm-v1") -> None:
        self._model_name = model_name
        self.calls: list[str] = []

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(self, request: GenerateRequest) -> GenerationResult:
        self.calls.append("generate")
        text = f"echo:{request.prompt}"
        structured: Mapping[str, Any] | None = None
        if request.structured_output is not None:
            structured = {"answer": text, "schema_title": request.structured_output.get("title")}
        return GenerationResult(
            text=text,
            model_name=self._model_name,
            usage=UsageMetadata(prompt_tokens=3, completion_tokens=5, total_tokens=8),
            structured=structured,
            finish_reason="stop",
        )

    def chat(self, request: ChatRequest) -> GenerationResult:
        self.calls.append("chat")
        joined = " | ".join(f"{m.role}:{m.content}" for m in request.messages)
        return GenerationResult(
            text=joined,
            model_name=self._model_name,
            usage=UsageMetadata(prompt_tokens=10, completion_tokens=4, total_tokens=14),
            finish_reason="stop",
        )


def test_package_exports_language_model_provider() -> None:
    assert LanguageModelProvider is BaseLanguageModelProvider


def test_fake_provider_generate_and_usage() -> None:
    provider: LanguageModelProvider = FakeLanguageModelProvider()
    result = provider.generate(GenerateRequest(prompt="muscle atrophy in microgravity"))
    assert result.model_name == "fake-llm-v1"
    assert result.text.startswith("echo:")
    assert result.usage is not None
    assert result.usage.total_tokens == 8
    assert provider.calls == ["generate"]


def test_fake_provider_chat_and_structured_option() -> None:
    provider = FakeLanguageModelProvider()
    chat = provider.chat(
        ChatRequest(
            messages=[
                ChatMessage(role="system", content="Ground answers in evidence."),
                ChatMessage(role="user", content="What happens to muscle?"),
            ]
        )
    )
    assert "system:" in chat.text
    assert "user:" in chat.text

    structured = provider.generate(
        GenerateRequest(
            prompt="summarize",
            structured_output={"title": "GroundedAnswer", "type": "object"},
        )
    )
    assert structured.structured is not None
    assert structured.structured["schema_title"] == "GroundedAnswer"


def test_incomplete_provider_cannot_be_instantiated() -> None:
    class IncompleteProvider(LanguageModelProvider):
        @property
        def model_name(self) -> str:
            return "incomplete"

        def generate(self, request: GenerateRequest) -> GenerationResult:
            return GenerationResult(text="", model_name=self.model_name)

    with pytest.raises(TypeError):
        IncompleteProvider()  # type: ignore[abstract]


def test_interface_module_has_no_provider_specific_imports() -> None:
    source = INTERFACE_MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(INTERFACE_MODULE))
    imported: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".", maxsplit=1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", maxsplit=1)[0])

    forbidden = imported & _FORBIDDEN_IMPORT_ROOTS
    assert not forbidden, f"provider-specific imports in interface module: {sorted(forbidden)}"


def test_usage_metadata_fields_are_optional() -> None:
    usage = UsageMetadata()
    assert usage.prompt_tokens is None
    assert usage.completion_tokens is None
    assert usage.total_tokens is None
    assert dict(usage.extra) == {}
