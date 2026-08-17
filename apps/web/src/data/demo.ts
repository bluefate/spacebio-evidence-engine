/** Demo links shown on the home page (issue #183). Questions match #26 / HOW_TO_DEMO. */

export const DEMO_SEARCH_TERMS: readonly string[] = [
  "ISS",
  "astronaut",
  "hindlimb unloading",
  "engineered",
  "proteome",
  "radiation",
  "0.33",
  "LIPUS",
  "extracellular vesicles",
  "soleus",
];

export const DEMO_ASK_QUESTIONS: readonly { id: string; question: string }[] = [
  {
    id: "rq_01",
    question:
      "What skeletal muscle proteome changes were reported in astronauts after ISS spaceflight?",
  },
  {
    id: "rq_02",
    question:
      "How does hindlimb unloading alter skeletal muscle in mouse models of simulated microgravity?",
  },
  {
    id: "rq_03",
    question:
      "What effects does simulated microgravity have on 3D engineered skeletal muscle myogenesis and contractile function?",
  },
  {
    id: "rq_04",
    question:
      "What mechanisms of skeletal muscle atrophy in microgravity are summarized in recent reviews, and which countermeasures are discussed?",
  },
  {
    id: "rq_05",
    question:
      "How do real spaceflight findings on human skeletal muscle compare with hindlimb-unloading mouse models of simulated microgravity?",
  },
  {
    id: "rq_06",
    question:
      "Do different partial-gravity levels (for example ~0.33g vs ~0.67g) produce different skeletal muscle outcomes in available studies?",
  },
  {
    id: "rq_07",
    question:
      "How do radiation plus unloading models differ from unloading alone for skeletal muscle outcomes in rodents?",
  },
  {
    id: "rq_08",
    question:
      "What is the recommended clinical drug regimen to reverse astronaut sarcopenia during a Mars transit?",
  },
  {
    id: "rq_09",
    question:
      "Did microgravity exposure change cardiac ejection fraction in the August MVP skeletal-muscle corpus?",
  },
  {
    id: "rq_10",
    question:
      "What interventions or countermeasures (exercise preconditioning, ultrasound, extracellular vesicles, or similar) have been tested against unloading- or microgravity-related muscle atrophy in the corpus?",
  },
];

export function searchDemoHref(term: string): string {
  return `/search?q=${encodeURIComponent(term)}`;
}

export function askDemoHref(question: string): string {
  return `/ask?q=${encodeURIComponent(question)}`;
}
