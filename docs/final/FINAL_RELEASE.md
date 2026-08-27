# Final Release and Submission Guide

## Space Biology Evidence Engine

**Release:** August 2026 MVP  
**Prepared by:** John Hernandez (`jherna65@fau.edu`)  
**Sponsor:** FAU AI HootCamp  
**Primary repository:** <https://github.com/bluefate/spacebio-evidence-engine>  
**GitHub Classroom repository:** <https://github.com/FAU-AI-HootCamp-Summer-2026/buildphase-bluefate>

![Space Biology Evidence Engine](../brand/logo-wordmark.png)

## 1. Release summary

The Space Biology Evidence Engine is a local-first, citation-first retrieval-augmented workspace for searching, comparing, and synthesizing evidence from a controlled corpus of 23 owner-approved open-access publications about microgravity and skeletal muscle.

The release addresses a specific research problem: relevant space-biology publications are difficult to search, compare, and synthesize while preserving study context and passage-level provenance. The system combines PDF ingestion, local embeddings, PostgreSQL/pgvector retrieval, optional keyword/hybrid retrieval, grounded answer generation, citation validation, and a minimal Next.js research interface.

The MVP is complete and ready for repository-based evaluation and a local demonstration. The complete presentation, one-page summary, screenshots, documentation, and backup demo materials are included for submission.

## 2. Intended users

- Space-biology researchers investigating microgravity and skeletal-muscle evidence.
- Students and educators who need inspectable scientific sources.
- Corpus maintainers curating approved open-access literature.
- Technical reviewers evaluating retrieval, grounding, provenance, and scientific safeguards.

## 3. Delivered capabilities

### Application

- Next.js research interface with Home, Ask, Search, Corpus, Publication, Compare, Add Paper, and indexing workflows.
- FastAPI service with health, search, Ask, diagnostics, and publication-management endpoints.
- PostgreSQL with pgvector, SQLAlchemy models, and Alembic migrations.
- Docker Compose local infrastructure.

### Data and retrieval

- Controlled inventory of 23 approved open-access publications.
- Automated PDF download for approved inventory records.
- PDF extraction, quality checks, chunking, embedding, and reprocessing.
- Semantic vector retrieval, PostgreSQL full-text retrieval, hybrid fusion, metadata filtering, and optional reranking.
- Preservation of publication ID, title, section, page, source URL, and chunk provenance.

### AI and grounding

- Local Sentence Transformer embeddings.
- Provider-neutral language-model interface.
- OpenAI chat provider behind `OPENAI_API_KEY`.
- Local Ollama development path.
- Evidence-sufficiency checks before generation.
- Passage-level citation validation after generation.
- Explicit insufficient-evidence behavior instead of model-memory fallback.

### Quality and governance

- Python and web test suites covering ingestion, retrieval, citations, APIs, UI rendering, and accessibility.
- Ruff linting and formatting, Pyright checking, Node type checking, and CI workflows.
- Retrieval, hallucination, citation-correctness, and graph-extraction evaluation harnesses.
- License review, PDF quality assessment, security guidance, cost controls, and documented architectural decisions.

## 4. Architecture

```text
Approved OA PDFs
      |
      v
PDF fetch + quality review
      |
      v
Extract -> chunk -> embed
      |
      v
PostgreSQL + pgvector
      |
      v
Semantic / full-text / hybrid retrieval
      |
      v
Evidence sufficiency gate
      |
      v
OpenAI or Ollama generation
      |
      v
Citation validation -> GroundedAnswerResponse
      |
      v
Next.js citation-first research UI
```

Detailed diagrams and design decisions are available in [`design.md`](../../design.md), [`ARCHITECTURE.md`](../architecture/ARCHITECTURE.md), and [`RAG_ARCHITECTURE.md`](../architecture/RAG_ARCHITECTURE.md).

## 5. Demo walkthrough

### Prerequisites

- Python 3.12 or newer.
- Node.js 22 or newer.
- Docker Desktop.
- Optional Ollama or OpenAI API access for generated answers.

### Start the application

```bash
cp .env.example .env
make setup
make setup-check
make fetch-pdfs
make ingest
make api
make web
```

Open <http://localhost:3000>.

For a local LLM path, follow [`HOW_TO_DEMO.md`](../operations/HOW_TO_DEMO.md). For detailed setup and troubleshooting, follow [`LOCAL_SETUP.md`](../operations/LOCAL_SETUP.md).

### Suggested flow

1. **Home:** introduce the controlled corpus and demo links.
2. **Corpus:** show the 23 approved records, license labels, organism, exposure, and ingest state.
3. **Publication details:** show DOI, source URL, license, model system, and provenance.
4. **Search:** search catalog metadata and indexed passages.
5. **Compare:** place human, animal, and engineered-tissue records side by side without merging their evidence.
6. **Ask:** submit a reference question and inspect the grounded answer, citation markers, and quoted supporting passages.
7. **Insufficient evidence:** ask an unsupported question and show that the system declines instead of guessing.

## 6. Screenshots

| Area | Screenshot |
| --- | --- |
| Home and demo entry points | [`01-home.png`](screenshots/01-home.png) |
| Grounded Ask form | [`02-ask.png`](screenshots/02-ask.png) |
| Search workspace | [`03-search.png`](screenshots/03-search.png) |
| Controlled corpus | [`04-corpus.png`](screenshots/04-corpus.png) |
| Study comparison | [`05-compare.png`](screenshots/05-compare.png) |
| Publication provenance | [`06-publication.png`](screenshots/06-publication.png) |

## 7. Final artifacts

| Artifact | Location | Status |
| --- | --- | --- |
| Pitch deck (PowerPoint, 12 slides with speaker notes) | [`Space_Biology_Evidence_Engine_Pitch_Deck.pptx`](Space_Biology_Evidence_Engine_Pitch_Deck.pptx) | Complete |
| Pitch deck (PDF) | [`Space_Biology_Evidence_Engine_Pitch_Deck.pdf`](Space_Biology_Evidence_Engine_Pitch_Deck.pdf) | Complete |
| One-page project summary (PowerPoint) | [`Space_Biology_Evidence_Engine_One_Page_Summary.pptx`](Space_Biology_Evidence_Engine_One_Page_Summary.pptx) | Complete |
| One-page project summary (PDF) | [`Space_Biology_Evidence_Engine_One_Page_Summary.pdf`](Space_Biology_Evidence_Engine_One_Page_Summary.pdf) | Complete |
| Final release/submission document | This document and [`FINAL_RELEASE.pdf`](FINAL_RELEASE.pdf) | Complete |
| Demo video | README placeholder; external accessible URL to be added after recording | Pending |
| Project plan | [`plan.md`](../../plan.md) | Complete |
| Technical design | [`design.md`](../../design.md) | Complete |

## 8. Verification

Primary repository quality gates:

```bash
make lint
make typecheck
make test
make test-web
make validate
```

The project includes CI checks for Python linting, Python type checking, Python tests, and Node checks. No secrets, API keys, credentials, `.env` files, or publication PDFs should be committed.

## 9. Security and scientific integrity

- Publication content is treated as untrusted input and is never executed.
- Downloaded PDFs are validated before processing.
- API keys remain in local environment variables.
- The LLM is not called when retrieved evidence is insufficient.
- Generated citation markers must match retrieved chunks.
- Human, animal, tissue, cell, and engineered-system evidence remain labeled.
- The system does not convert correlations to causation or invent cross-study findings.
- Scientific outputs require human review before being treated as validated conclusions.

## 10. Known limitations

- The application is local-first and does not currently have a public production deployment URL.
- Grounded Ask requires indexed PDFs and a configured OpenAI or Ollama provider.
- Corpus coverage is intentionally limited to microgravity and skeletal muscle.
- Search quality depends on corpus extraction and embedding quality.
- Scientific correctness evaluation includes fixtures and human-review fields but is not a substitute for expert review.
- Graph extraction is experimental; the MVP deliberately does not add a graph database.
- The final demo video has not yet been recorded and will be completed as a separate finalization step.

## 11. Future improvements

- Expand the corpus through a reviewed registration and approval workflow.
- Add production hosting, authentication, and persistent operational monitoring.
- Run larger retrieval benchmarks with expert relevance judgments.
- Add structured reviewer sign-off for generated answers.
- Improve comparison with validated structured study outcomes.
- Continue evaluating graph extraction without introducing graph-native persistence prematurely.

## 12. Demo backup plan

If Docker, model weights, network access, or showcase equipment fails:

1. Open the PDF pitch deck locally.
2. Use the committed screenshots to walk through Home, Ask, Search, Corpus, Compare, and Publication details.
3. Explain the expected Ask response using the documented grounding and citation-validation flow.
4. Open the repository documentation and evaluation artifacts locally.
5. Use the demo video after it is recorded and linked.

## 13. Common Q&A

**Why not use a general chatbot?**  
A general chatbot does not enforce the controlled corpus or passage-level provenance. This system retrieves approved evidence first and fails closed when evidence is missing.

**How are hallucinations reduced?**  
The service evaluates evidence sufficiency before generation and validates generated citation markers against retrieved chunks afterward. Unsupported outputs are rejected.

**Why is the corpus small?**  
The MVP prioritizes curation, licensing, extractability, and provenance over volume. The controlled boundary makes evaluation and scientific review practical.

**Why local-first?**  
Local operation supports privacy, cost control, reproducibility, and optional use of Ollama. OpenAI remains available as a configured provider.

**Is the AI output scientifically validated?**  
No model output is automatically treated as validated science. The interface preserves source evidence and limitations so a human can review it.

## 14. Submission checklist

- [x] Final application code and documentation are in the repository.
- [x] Pitch deck is committed as PowerPoint and PDF.
- [x] Pitch deck contains 12 slides and speaker notes.
- [x] One-page project summary is committed as PowerPoint and PDF.
- [x] Project summary includes name, email, sponsor, purpose, users, status, capabilities, readiness, and participation status.
- [x] Architecture, API, setup, deployment, limitations, evaluation, security, and cost documentation are linked.
- [x] Demo screenshots and a backup plan are committed.
- [x] `plan.md` and `design.md` are linked.
- [ ] Demo video is recorded, captioned, uploaded, and linked from README.
- [ ] A public deployed application URL is supplied, if required; current release is local-first.
- [ ] Final Classroom repository is synchronized with the principal repository after approval.
- [ ] Canvas submission contains the GitHub Classroom repository URL.

## 15. Submission status

The final application, pitch deck, one-page summary, technical documentation, screenshots, and release package are provided for project submission and evaluation.
