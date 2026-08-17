import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RetrievalDiagnosticsClient } from "./RetrievalDiagnosticsClient";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("RetrievalDiagnosticsClient", () => {
  it("shows chunk IDs and scores from the diagnostics API", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          query_sha256: "abc123",
          query_length: 12,
          top_k: 8,
          search_algorithm: "semantic_vector",
          score_kind: "cosine_similarity",
          embedding_model: "fixture-embedding",
          embedding_dimension: 384,
          result_count: 1,
          selected_citation_ids: ["C1"],
          selected_chunks: [
            {
              citation_id: "C1",
              rank: 1,
              chunk_id: "chk_soleus_001",
              score: 0.9123,
              publication_id: "pub_001",
              section: "results",
              page_start: 4,
              page_end: 4,
              source_url: "https://doi.org/10.1038/example",
              embedding_model: "fixture-embedding",
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    render(<RetrievalDiagnosticsClient />);
    fireEvent.change(screen.getByLabelText("Research question"), {
      target: { value: "How does microgravity affect skeletal muscle?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Inspect retrieval" }));

    await waitFor(() => {
      expect(screen.getByText("chk_soleus_001")).toBeInTheDocument();
    });
    expect(screen.getByText("0.9123")).toBeInTheDocument();
    expect(screen.getAllByText("C1").length).toBeGreaterThan(0);
    expect(screen.queryByText("sk-secret")).not.toBeInTheDocument();
  });
});
