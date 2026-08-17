/** Fetch helper for gated developer retrieval diagnostics (issue #67). */

export type RetrievalDiagnosticsChunk = {
  citation_id: string;
  rank: number;
  chunk_id: string;
  score: number;
  publication_id: string;
  section: string;
  page_start: number | null;
  page_end: number | null;
  source_url: string;
  embedding_model: string;
};

export type RetrievalDiagnosticsResponse = {
  query_sha256: string;
  query_length: number;
  top_k: number;
  search_algorithm: string;
  score_kind: string;
  embedding_model: string;
  embedding_dimension: number;
  result_count: number;
  selected_chunks: RetrievalDiagnosticsChunk[];
  selected_citation_ids: string[];
};

export type DiagnosticsError = {
  message: string;
  status?: number;
};

export async function fetchRetrievalDiagnostics(request: {
  question: string;
  top_k?: number;
}): Promise<{ response?: RetrievalDiagnosticsResponse; error?: DiagnosticsError }> {
  const payload = {
    question: request.question.trim(),
    top_k: request.top_k ?? 8,
  };

  try {
    const result = await fetch("/api/dev/retrieval-diagnostics", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });

    if (!result.ok) {
      const body = await result.json().catch(() => ({
        detail: `Request failed with status ${result.status}`,
      }));
      return {
        error: {
          message: body.detail ?? `Request failed with status ${result.status}`,
          status: result.status,
        },
      };
    }

    return { response: (await result.json()) as RetrievalDiagnosticsResponse };
  } catch {
    return {
      error: {
        message:
          "Retrieval diagnostics are unavailable. Enable the developer flag and start the API.",
      },
    };
  }
}
