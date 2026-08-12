"""Unit tests for grounded-answer prompt rendering (issue #53)."""

from __future__ import annotations

from spacebio_evidence_engine.rag import (
    GROUNDED_ANSWER_PROMPT_VERSION,
    assemble_context,
    render_grounded_answer_prompt,
)
from spacebio_evidence_engine.rag.prompt import (
    grounded_answer_template_path,
    load_grounded_answer_template,
)
from spacebio_evidence_engine.retrieval import SemanticSearchHit


def _hit(chunk_id: str, text: str) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=0.91,
        publication_id="pub_001",
        title="Microgravity skeletal muscle study",
        section="results",
        chunk_text=text,
        source_url="https://doi.org/10.0/example",
        page_start=2,
        page_end=2,
        section_heading="Results",
        model_name="fixture-model",
    )


def test_grounded_answer_template_is_versioned_in_repo() -> None:
    path = grounded_answer_template_path()
    assert path.name == f"grounded_answer_v{GROUNDED_ANSWER_PROMPT_VERSION}.md"
    assert path.is_file()
    raw = load_grounded_answer_template()
    assert f"version: {GROUNDED_ANSWER_PROMPT_VERSION}" in raw
    assert "prompt_id: grounded_answer" in raw


def test_render_grounded_answer_prompt_structure() -> None:
    context = assemble_context(
        [_hit("chk_a", "Soleus mass decreased in flight animals.")],
        token_budget=500,
    )
    prompt = render_grounded_answer_prompt(
        "How does microgravity affect soleus mass?",
        context,
    )

    assert prompt.version == GROUNDED_ANSWER_PROMPT_VERSION
    assert prompt.prompt_id == "grounded_answer"
    assert "Use only the retrieved evidence" in prompt.system
    assert "insufficient" in prompt.system.lower()
    assert "Do not give medical advice" in prompt.system
    assert "mission operations recommendations" in prompt.system
    assert "How does microgravity affect soleus mass?" in prompt.user
    assert "chunk_id=chk_a" in prompt.user
    assert "Soleus mass decreased" in prompt.user
    assert "{{" not in prompt.prompt_text

    generate_request = prompt.to_generate_request()
    assert generate_request.system == prompt.system
    assert generate_request.prompt == prompt.user

    chat_request = prompt.to_chat_request()
    assert chat_request.messages[0].role == "system"
    assert chat_request.messages[1].role == "user"
    assert chat_request.messages[1].content == prompt.user


def test_template_forbids_recommendation_language() -> None:
    raw = load_grounded_answer_template().lower()
    assert "do not give medical advice" in raw
    assert "mission operations recommendations" in raw
    # Must not encourage advice as a desired behavior.
    assert "you should prescribe" not in raw
    assert "recommend a treatment plan" not in raw
    assert "recommend a mission" not in raw
