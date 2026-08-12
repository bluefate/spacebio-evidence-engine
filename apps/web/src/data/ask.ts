/** Types and fetch helper for the grounded /ask API (issue #62). */

export type AskRequest = {
  question: string;
  top_k?: number;
};

export type SufficiencyStatus = "sufficient" | "insufficient" | "marginal";

export type EvidenceSufficiency = {
  status: SufficiencyStatus;
  reason: string | null;
  retrieved_chunk_count: number;
  supporting_publication_count: number;
};

export type PassageCitation = {
  citation_id: string;
  chunk_id: string;
  publication_id: string;
  title?: string | null;
  section?: string | null;
  page?: number | null;
  source_url?: string | null;
  excerpt?: string | null;
};

export type AnswerClaim = {
  claim_id: string;
  text: string;
  citation_ids: string[];
};

export type GroundedAnswerResponse = {
  schema_version: string;
  question: string;
  answer_text: string;
  claims: AnswerClaim[];
  citations: PassageCitation[];
  sufficiency: EvidenceSufficiency;
  limitations?: Array<{ text: string; citation_ids?: string[] }>;
  conflicts?: Array<{ summary: string; citation_ids?: string[] }>;
  warnings?: Array<{ code: string; message: string }>;
  model_name?: string | null;
};

export type AskError = {
  message: string;
  status?: number;
};

export async function askQuestion(
  request: AskRequest,
): Promise<{ response?: GroundedAnswerResponse; error?: AskError }> {
  const payload: AskRequest = {
    question: request.question.trim(),
    top_k: request.top_k ?? 8,
  };

  try {
    const result = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });

    if (!result.ok) {
      const body = await result.json().catch(() => ({ detail: `Request failed with status ${result.status}` }));
      return {
        error: {
          message: body.detail ?? `Request failed with status ${result.status}`,
          status: result.status,
        },
      };
    }

    return { response: (await result.json()) as GroundedAnswerResponse };
  } catch {
    return {
      error: {
        message:
          "The grounded answer service is unavailable. Start the API with make api and try again.",
      },
    };
  }
}
