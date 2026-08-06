# August MVP Corpus Inventory

## Purpose
Propose the initial controlled corpus for the August 2026 MVP (issue [#20](https://github.com/bluefate/spacebio-evidence-engine/issues/20)).

## Status
**Owner-approved** (issue [#20](https://github.com/bluefate/spacebio-evidence-engine/issues/20) closed; manifest `human_approval=approved`). Ingest may proceed subject to per-item license/PDF QA.

## Topic
Microgravity and skeletal muscle (approved D1).

## License and use policy (important)

The Space Biology Evidence Engine is a **non-commercial**, educational / research citation-first evidence system for the AI HootCamp Build Phase and related learning use.

| Allowed corpus licenses | How we use them |
|-------------------------|-----------------|
| **CC BY** | Preferred. Attribute; retrieve; quote passages; link to source. |
| **CC BY-NC-ND** | Allowed because this tool is **non-commercial**. Attribute; retrieve; quote passages for answers; link to original DOI/PDF. Do **not** redistribute full articles as a commercial product, sell the corpus, or publish adapted full-text derivatives. |

**Operational rules**

1. Record `license` per publication in the manifest (never assume).
2. Answers must cite passages and preserve links to the original work (BY).
3. Do not ship a standalone commercial republishing of NC-ND full texts.
4. If the project later becomes commercial, **re-review NC-ND items** before continued use or remove them.
5. Paywalled or unclear-rights works remain excluded.
The manifest now records `access_restriction_notes` and `redistribution_notes` for each publication, derived from the license identifier by `spacebio_evidence_engine.corpus.licenses.classify_license`. These fields operationalize the D10 license policy and make redistribution constraints explicit before ingestion.


## Selection summary

| Metric | Value |
|--------|-------|
| Approved count | **23** |
| CC BY | 17 |
| CC BY-NC-ND | 6 |
| Topic | microgravity_skeletal_muscle |
| Machine-readable manifest | [august_mvp_corpus_manifest.csv](../../data/inventory/august_mvp_corpus_manifest.csv) |

## Inclusion / exclusion checklist

| Check | Result |
|-------|--------|
| Open-access with recorded license | Pass |
| On approved topic | Pass |
| Extractable methods/results/findings (or citable methods/design for mission papers) | Pass |
| Sufficient citation metadata | Pass |
| Paywalled / unclear rights | Excluded |
| Non-scientific commentary | Excluded |

## Proposed publications

| ID | Year | License | Model | Exposure | Title | DOI |
|----|------|---------|-------|----------|-------|-----|
| pub_001 | 2024 | CC BY | human | spaceflight | Spaceflight on the ISS changed the skeletal muscle proteome of two astronauts | [10.1038/s41526-024-00406-3](https://doi.org/10.1038/s41526-024-00406-3) |
| pub_002 | 2023 | CC BY | mouse | simulated microgravity | Genetic diversity modulates the physical and transcriptomic response of skeletal muscle to simulated microgravity in male mice | [10.1038/s41526-023-00334-8](https://doi.org/10.1038/s41526-023-00334-8) |
| pub_003 | 2024 | CC BY | engineered tissue | simulated microgravity | Simulated microgravity attenuates myogenesis and contractile function of 3D engineered skeletal muscle tissues | [10.1038/s41526-024-00353-z](https://doi.org/10.1038/s41526-024-00353-z) |
| pub_004 | 2023 | CC BY | mouse | HU + radiation | Myeloid cell infiltration in skeletal muscle after combined hindlimb unloading and radiation exposure in mice | [10.1038/s41526-023-00289-w](https://doi.org/10.1038/s41526-023-00289-w) |
| pub_005 | 2023 | CC BY | mouse | HU + radiation | Impacts of radiation exposure, hindlimb unloading, and recovery on murine skeletal muscle cell telomere length | [10.1038/s41526-023-00303-1](https://doi.org/10.1038/s41526-023-00303-1) |
| pub_006 | 2021 | CC BY | multi | review | Update on the effects of microgravity on the musculoskeletal system | [10.1038/s41526-021-00158-4](https://doi.org/10.1038/s41526-021-00158-4) |
| pub_007 | 2024 | CC BY | multi | review | Mechanisms and Countermeasures for Muscle Atrophy in Microgravity | [10.3390/cells13242120](https://doi.org/10.3390/cells13242120) |
| pub_008 | 2024 | CC BY | human | spaceflight | Nitrosative Stress in Astronaut Skeletal Muscle in Spaceflight | [10.3390/antiox13040432](https://doi.org/10.3390/antiox13040432) |
| pub_009 | 2024 | CC BY | rat | hindlimb suspension | Molecular Signaling Effects behind the Spontaneous Soleus Muscle Activity Induced by 7-Day Rat Hindlimb Suspension | [10.3390/ijms25158316](https://doi.org/10.3390/ijms25158316) |
| pub_010 | 2023 | CC BY | rodent | hindlimb unloading | New Findings: Hindlimb Unloading Causes Nucleocytoplasmic Ca2+ Overload and DNA Damage in Skeletal Muscle | [10.3390/cells12071077](https://doi.org/10.3390/cells12071077) |
| pub_011 | 2022 | CC BY | mouse | spaceflight | Detection of Target Genes for Drug Repurposing to Treat Skeletal Muscle Atrophy in Mice Flown in Spaceflight | [10.3390/genes13030473](https://doi.org/10.3390/genes13030473) |
| pub_012 | 2018 | CC BY | mouse | hindlimb suspension | Exercise preconditioning diminishes skeletal muscle atrophy after hindlimb suspension in mice | [10.1152/japplphysiol.00137.2018](https://doi.org/10.1152/japplphysiol.00137.2018) |
| pub_013 | 2021 | CC BY | rat | hindlimb unloading | Molecular and Metabolic Mechanism of Low-Intensity Pulsed Ultrasound Improving Muscle Atrophy in Hindlimb Unloading Rats | [10.3390/ijms222212112](https://doi.org/10.3390/ijms222212112) |
| pub_014 | 2026 | CC BY | mouse | spaceflight partial-g | 0.33 g mitigates muscle atrophy while 0.67 g preserves muscle function and myofiber type composition in mice during spaceflight | [10.1126/sciadv.aed2258](https://doi.org/10.1126/sciadv.aed2258) |
| pub_015 | 2026 | CC BY | rat | partial weight bearing | Estrogen Receptor Alpha (ERα) Is Involved in Resveratrol-Mediated Muscle Preservation During Mechanical Unloading in Male Rats | [10.3390/muscles5020023](https://doi.org/10.3390/muscles5020023) |
| pub_016 | 2026 | CC BY | engineered human muscle | ISS | MicroAge mission: experimental design and hardware for a bespoke culture system supporting tissue-engineered skeletal muscle | [10.1038/s41526-026-00579-z](https://doi.org/10.1038/s41526-026-00579-z) |
| pub_017 | 2026 | CC BY-NC-ND | multi | modeling | Integrated cross-species translation and biophysical multi-scale modeling links molecular signatures and locomotory phenotypes in spaceflight-induced sarcopenia | [10.1038/s41526-025-00557-x](https://doi.org/10.1038/s41526-025-00557-x) |
| pub_018 | 2026 | CC BY-NC-ND | human EVs → mouse HU | hindlimb unloading | Human plasma extracellular vesicles as an exercise mimetic to preserve skeletal muscle plasticity during disuse | [10.1038/s41526-026-00582-4](https://doi.org/10.1038/s41526-026-00582-4) |
| pub_019 | 2025 | CC BY-NC-ND | human engineered muscle | ISS | Microgravity accelerates skeletal muscle degeneration: Functional and transcriptomic insights from an ISS muscle lab-on-chip model | [10.1016/j.stemcr.2025.102550](https://doi.org/10.1016/j.stemcr.2025.102550) |
| pub_020 | 2025 | CC BY-NC-ND | mouse | flight vs HU | Simulated microgravity accurately models long-duration spaceflight effects on bone and skeletal muscle in skeletally immature mice | [10.1016/j.bonr.2025.101871](https://doi.org/10.1016/j.bonr.2025.101871) |
| pub_021 | 2025 | CC BY-NC-ND | mouse | simulated microgravity | Abdominal LIPUS ameliorates simulated microgravity induced skeletal muscle atrophy via the gut-muscle axis | [10.1038/s41526-025-00514-8](https://doi.org/10.1038/s41526-025-00514-8) |
| pub_022 | 2025 | CC BY-NC-ND | mouse / C2C12 | hindlimb unloading | hBMSC-EVs alleviate weightlessness-induced skeletal muscle atrophy by suppressing oxidative stress and inflammation | [10.1186/s13287-025-04175-y](https://doi.org/10.1186/s13287-025-04175-y) |
| pub_023 | 2025 | CC BY | mouse | hindlimb unloading | Mouse hindlimb unloading, as a model of simulated microgravity, leads to dysregulated iron homeostasis in liver and skeletal muscle cells | [10.1016/j.lssr.2025.01.003](https://doi.org/10.1016/j.lssr.2025.01.003) |

## Hold (not added yet)

None currently.

## Human approval request

Please review the proposed list on [#20](https://github.com/bluefate/spacebio-evidence-engine/issues/20) and approve it as the August MVP corpus (or request DOI swaps).

**How to approve (owner):**

1. Spot-check a few DOIs/licenses if desired (especially NC-ND rows and Elsevier hybrid OA).
2. Comment on [#20](https://github.com/bluefate/spacebio-evidence-engine/issues/20) with an explicit approval, for example:
   > **Approved** — August MVP corpus list accepted as in `data/inventory/august_mvp_corpus_manifest.csv` (including pub_023).
3. In a follow-up PR (or ask an agent), set every row’s `human_approval` from `pending` → `approved` in the CSV and matching `approval` fields in `apps/web/src/data/corpus.json`, and change this document’s **Status** to **Approved**.
4. Issue #20 is already closed for delivery of the inventory artifact; list approval is recorded by that comment + the `human_approval=approved` manifest update.

After approval: proceed to PDF staging / ingest.

## Related documents
- [Corpus specification](CORPUS_SPECIFICATION.md)
- [Decision log](../governance/DECISION_LOG.md) (D10)
- [Metadata schema](METADATA_SCHEMA.md)
- [GitHub Project board](https://github.com/users/bluefate/projects/6)
- [Issue #20](https://github.com/bluefate/spacebio-evidence-engine/issues/20)
- Rah et al. (2025): [https://doi.org/10.1016/j.lssr.2025.01.003](https://doi.org/10.1016/j.lssr.2025.01.003)
