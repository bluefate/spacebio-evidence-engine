# How to demo (script)

## Purpose

A click-through script for a local demo or smoke test. **Questions reuse the owner-approved set from issue #26.** Expected answers here are **behavior checks** (which publications should be cited, when to refuse), not invented study results.

Machine-readable questions: [`evals/fixtures/reference_questions.json`](../../evals/fixtures/reference_questions.json). Scientific notes: [REFERENCE_QUESTIONS.md](../rag/REFERENCE_QUESTIONS.md).

## Start the app (two windows)

From the repo root. Stop servers with **Ctrl-C**, not Ctrl-Z.

**Window 1** (first time; this returns):

```bash
cp .env.example .env
make setup
make api
```

**Window 2** (new terminal, same folder):

```bash
make web
```

Open [http://localhost:3000](http://localhost:3000).

Optional, before Ask/passage Search: on **Corpus** or **Home**, click **Download missing PDFs** (same as `make fetch-pdfs`), then `make ingest`. Also `pip install -e ".[embeddings]"` and local **Ollama**. Default model is `llama3.2:1b` (fast); for citation-following demos use `OLLAMA_MODEL=llama3.2:3b` or OpenAI. Without ingest + a chat model, Ask should **fail closed**, not guess.

## What to click first (no ingest required)

| Step | Page | Pass if |
| --- | --- | --- |
| 1 | Home | Ask, Search, Corpus, Compare, Add paper |
| 2 | Corpus | 23 cards; DOI links; organism and exposure labels |
| 3 | Compare | Human vs mouse labels only — no invented “this study found more atrophy” |
| 4 | Add paper | DOI / PDF / Index are separate; Index is not training |

## 10 search terms (Search page)

Type each term on [http://localhost:3000/search](http://localhost:3000/search). **Catalog hits** come from inventory titles and labels (`corpus.json`) even before ingest. **Passage hits** appear only after `make ingest` and with the API running.

Do not treat a catalog title match as a grounded scientific answer.

| # | Search term | Expect catalog hit (at least) | Notes |
| ---: | --- | --- | --- |
| 1 | `ISS` | pub_001, pub_016, pub_019 | Spaceflight / ISS titles |
| 2 | `astronaut` | pub_001, pub_008 | Human spaceflight |
| 3 | `hindlimb unloading` | pub_004, pub_005, pub_010, pub_013, pub_018, pub_022, pub_023 | Simulated microgravity model |
| 4 | `engineered` | pub_003, pub_016, pub_019 | Tissue / lab-on-chip — **not** whole-organism flight |
| 5 | `proteome` | pub_001 | Prefer not to merge with mouse HU |
| 6 | `radiation` | pub_004, pub_005 | Combined stressor vs unloading alone |
| 7 | `0.33` | pub_014 | Partial gravity |
| 8 | `LIPUS` | pub_013, pub_021 | Ultrasound countermeasure papers |
| 9 | `extracellular vesicles` | pub_018, pub_022 | EV / exercise-mimetic rows |
| 10 | `soleus` | pub_009 | Rat hindlimb suspension |

**Pass:** each term returns at least one matching publication id/title. **Fail:** empty results for these inventory words, or the UI claiming a generated finding from a title match.

## 10 Ask questions (Ask page)

Use [http://localhost:3000/ask](http://localhost:3000/ask). Copy the **Question** column. After ingest + Ollama or OpenAI, the page should show a large **Answer** first, then **Supporting details** (claims, warnings, cited PDF quotes). Answers must cite passages. **Do not accept fluent text without citations.** Organism/model must stay labeled (human vs mouse vs engineered tissue).

These expected answers are **not** gold wording from the PDFs. If the model states a numeric finding, it must appear in a cited chunk.

| ID | Question | Expect | Candidate pubs | Pass if |
| --- | --- | --- | --- | --- |
| rq_01 | What skeletal muscle proteome changes were reported in astronauts after ISS spaceflight? | Answerable from **human spaceflight** evidence | pub_001, pub_008 | Cites astronaut/ISS muscle papers; does not treat mouse HU as astronaut data |
| rq_02 | How does hindlimb unloading alter skeletal muscle in mouse models of simulated microgravity? | Answerable from **mouse / HU** evidence | pub_002, pub_010, pub_012, pub_023 | Labels mouse/HU; does not call it ISS astronaut data |
| rq_03 | What effects does simulated microgravity have on 3D engineered skeletal muscle myogenesis and contractile function? | Answerable from **engineered tissue** | pub_003 | Labels engineered/in-vitro, not whole-organism flight |
| rq_04 | What mechanisms of skeletal muscle atrophy in microgravity are summarized in recent reviews, and which countermeasures are discussed? | Answerable as **review** evidence | pub_006, pub_007 | Treats reviews as secondary, not as a new experiment |
| rq_05 | How do real spaceflight findings on human skeletal muscle compare with hindlimb-unloading mouse models of simulated microgravity? | Comparison; keep models **separate** | pub_001, pub_002, pub_006, pub_020 | Explicit human vs mouse; no merged “the muscle” claim |
| rq_06 | Do different partial-gravity levels (for example ~0.33g vs ~0.67g) produce different skeletal muscle outcomes in available studies? | Answerable if pub_014 is ingested; else may be thin | pub_014 | If answered, cites partial-g study; if missing, insufficient — not Wikipedia |
| rq_07 | How do radiation plus unloading models differ from unloading alone for skeletal muscle outcomes in rodents? | Comparison of **combined vs unloading** | pub_004, pub_005 | Preserves radiation + HU conditions |
| rq_08 | What is the recommended clinical drug regimen to reverse astronaut sarcopenia during a Mars transit? | **Insufficient evidence** | none | Refuses / insufficient; **no** invented Mars drug protocol |
| rq_09 | Did microgravity exposure change cardiac ejection fraction in the August MVP skeletal-muscle corpus? | **Insufficient evidence** (off-topic) | none | Refuses; this corpus is skeletal muscle, not EF |
| rq_10 | What interventions or countermeasures (exercise preconditioning, ultrasound, extracellular vesicles, or similar) have been tested against unloading- or microgravity-related muscle atrophy in the corpus? | Answerable from intervention papers | pub_012, pub_013, pub_018, pub_021, pub_022 | Groups by intervention; no efficacy beyond cited passages |

**Without ingest or a chat model (Ollama / OpenAI):** the Ask UI/API failing closed (503 or a clear error) is a **pass**. A confident paragraph with no citations is a **fail**.

## Related documents

- [README — How to demo](../../README.md#how-to-demo)
- [Local setup](LOCAL_SETUP.md)
- [Corpus inventory](../data/CORPUS_INVENTORY.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
