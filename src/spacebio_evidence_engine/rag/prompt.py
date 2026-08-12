"""Versioned grounded-answer prompt templates (issue #53)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from spacebio_evidence_engine.llm.base import ChatMessage, ChatRequest, GenerateRequest
from spacebio_evidence_engine.rag.context import ContextAssemblyResult

GROUNDED_ANSWER_PROMPT_ID = "grounded_answer"
GROUNDED_ANSWER_PROMPT_VERSION = "1.0.0"

_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)
_SECTION_RE = re.compile(
    r"^#\s+(System|User)\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class GroundedAnswerPrompt:
    """Rendered grounded-answer prompt ready for an LLM provider call."""

    prompt_id: str
    version: str
    system: str
    user: str

    @property
    def prompt_text(self) -> str:
        """Single-string prompt for ``generate`` backends."""

        return f"### System\n{self.system}\n\n### User\n{self.user}"

    def to_generate_request(
        self,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> GenerateRequest:
        return GenerateRequest(
            prompt=self.user,
            system=self.system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def to_chat_request(
        self,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatRequest:
        return ChatRequest(
            messages=(
                ChatMessage(role="system", content=self.system),
                ChatMessage(role="user", content=self.user),
            ),
            temperature=temperature,
            max_tokens=max_tokens,
        )


def grounded_answer_template_path(
    *,
    version: str = GROUNDED_ANSWER_PROMPT_VERSION,
) -> Path:
    """Return the repo path for the versioned grounded-answer template file."""

    filename = f"grounded_answer_v{version}.md"
    repo_root = Path(__file__).resolve().parents[3]
    candidate = repo_root / "prompts" / filename
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(f"grounded answer prompt template not found: {filename}")


def load_grounded_answer_template(
    *,
    version: str = GROUNDED_ANSWER_PROMPT_VERSION,
) -> str:
    """Load the raw versioned template markdown from the repo."""

    return _cached_template(version)


@lru_cache(maxsize=4)
def _cached_template(version: str) -> str:
    return grounded_answer_template_path(version=version).read_text(encoding="utf-8")


def render_grounded_answer_prompt(
    question: str,
    context: ContextAssemblyResult,
    *,
    version: str = GROUNDED_ANSWER_PROMPT_VERSION,
) -> GroundedAnswerPrompt:
    """Render the versioned grounded-answer prompt from assembled context."""

    if not question.strip():
        raise ValueError("question must be a non-empty string")

    raw = load_grounded_answer_template(version=version)
    meta, body = _parse_front_matter(raw)
    prompt_id = str(meta.get("prompt_id", GROUNDED_ANSWER_PROMPT_ID))
    prompt_version = str(meta.get("version", version))
    if prompt_version != version:
        raise ValueError(
            f"template version {prompt_version!r} does not match requested {version!r}"
        )

    _assert_template_policy(body)

    system, user_template = _split_system_user(body)
    evidence = context.evidence_text.strip() or "(no evidence blocks within budget)"
    user = (
        user_template.replace("{{question}}", question.strip())
        .replace("{{evidence}}", evidence)
        .replace("{{instructions}}", context.instructions)
    )
    if "{{" in user or "{{" in system:
        raise ValueError("rendered grounded-answer prompt still contains placeholders")

    return GroundedAnswerPrompt(
        prompt_id=prompt_id,
        version=prompt_version,
        system=system.strip(),
        user=user.strip(),
    )


def _parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    match = _FRONT_MATTER_RE.match(raw)
    if match is None:
        return {}, raw
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, match.group(2)


def _split_system_user(body: str) -> tuple[str, str]:
    matches = list(_SECTION_RE.finditer(body))
    if len(matches) < 2:
        raise ValueError("prompt template must contain # System and # User sections")
    labels = [match.group(1) for match in matches[:2]]
    if labels != ["System", "User"]:
        raise ValueError("prompt template sections must be # System then # User")
    system = body[matches[0].end() : matches[1].start()].strip()
    user = body[matches[1].end() :].strip()
    if not system or not user:
        raise ValueError("prompt template system/user sections must be non-empty")
    return system, user


def _assert_template_policy(body: str) -> None:
    lowered = body.lower()
    required_snippets = (
        "use only the retrieved evidence",
        "insufficient",
        "do not give medical advice",
        "mission operations recommendations",
        "citation",
    )
    missing = [snippet for snippet in required_snippets if snippet not in lowered]
    if missing:
        raise ValueError(
            "grounded-answer template missing required policy text: " + ", ".join(missing)
        )
