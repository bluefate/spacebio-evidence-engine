import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AskClient } from "./AskClient";

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(),
}));

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

function mockFetch(response: Response) {
  return vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(response);
}

const sufficientAnswer = {
  schema_version: "1.0.0",
  question: "How does microgravity affect skeletal muscle?",
  answer_text:
    "Microgravity induces muscle atrophy, particularly in antigravity muscles such as the soleus [C1].",
  claims: [
    {
      claim_id: "claim_1",
      text: "Microgravity induces muscle atrophy in antigravity muscles.",
      citation_ids: ["C1"],
    },
  ],
  citations: [
    {
      citation_id: "C1",
      chunk_id: "chk_soleus_001",
      publication_id: "pub_001",
      title: "Spaceflight and skeletal muscle",
      section: "Results",
      page: 4,
      source_url: "https://doi.org/10.1038/example",
      excerpt: "Soleus muscle mass declined after unloading in flight mice.",
    },
  ],
  sufficiency: {
    status: "sufficient",
    reason: null,
    retrieved_chunk_count: 1,
    supporting_publication_count: 1,
  },
  limitations: [],
  conflicts: [],
  warnings: [],
};

const insufficientAnswer = {
  schema_version: "1.0.0",
  question: "What is the effect of microgravity on plants?",
  answer_text: "",
  claims: [],
  citations: [],
  sufficiency: {
    status: "insufficient",
    reason:
      "The corpus focuses on skeletal muscle and does not contain plant studies.",
    retrieved_chunk_count: 0,
    supporting_publication_count: 0,
  },
  limitations: [],
  conflicts: [],
  warnings: [],
};

describe("AskClient", () => {
  beforeEach(() => {
    // suppress act warnings from async state updates in tests
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  it("submits the question to /api/ask and renders the answer", async () => {
    mockFetch(new Response(JSON.stringify(sufficientAnswer), { status: 200 }));
    render(<AskClient />);

    const textarea = screen.getByLabelText("Research question");
    fireEvent.change(textarea, {
      target: { value: "How does microgravity affect skeletal muscle?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

    await waitFor(() => {
      expect(screen.getByTestId("citation-linked-text")).toBeInTheDocument();
    });

    expect(screen.getByText("Answer")).toBeInTheDocument();
    expect(screen.getByText("The grounded answer")).toBeInTheDocument();
    expect(screen.getByText("Supporting details")).toBeInTheDocument();
    expect(screen.getByText("Claims")).toBeInTheDocument();
    expect(screen.getByTestId("citation-marker-C1")).toBeInTheDocument();
    expect(screen.getByTestId("evidence-panel")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Soleus muscle mass declined after unloading in flight mice.",
      ),
    ).toBeInTheDocument();
  });

  it("shows the insufficient-evidence state when sufficiency is insufficient", async () => {
    mockFetch(
      new Response(JSON.stringify(insufficientAnswer), { status: 200 }),
    );
    render(<AskClient />);

    const textarea = screen.getByLabelText("Research question");
    fireEvent.change(textarea, {
      target: { value: "What is the effect of microgravity on plants?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

    await waitFor(() => {
      expect(screen.getByText("Insufficient evidence")).toBeInTheDocument();
    });

    expect(
      screen.getByText(
        "The corpus focuses on skeletal muscle and does not contain plant studies.",
      ),
    ).toBeInTheDocument();
  });

  it("shows the default insufficient-evidence copy when the question is empty", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    render(<AskClient />);

    fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

    expect(fetchSpy).not.toHaveBeenCalled();
    expect(screen.getByText("Insufficient evidence")).toBeInTheDocument();
    expect(
      screen.getByText(
        "The corpus does not contain enough relevant evidence to answer this question confidently.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByTestId("citation-linked-text"),
    ).not.toBeInTheDocument();
    expect(screen.queryByTestId("evidence-panel")).not.toBeInTheDocument();
  });

  it("selecting a citation chip highlights the evidence panel item", async () => {
    mockFetch(new Response(JSON.stringify(sufficientAnswer), { status: 200 }));
    render(<AskClient />);

    const textarea = screen.getByLabelText("Research question");
    fireEvent.change(textarea, {
      target: { value: "How does microgravity affect skeletal muscle?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

    await waitFor(() => {
      expect(screen.getByTestId("evidence-item-C1")).toHaveAttribute(
        "data-active",
        "true",
      );
    });
  });

  it("shows an error message when the API request fails", async () => {
    mockFetch(
      new Response(JSON.stringify({ detail: "Service unavailable" }), {
        status: 503,
      }),
    );
    render(<AskClient />);

    const textarea = screen.getByLabelText("Research question");
    fireEvent.change(textarea, { target: { value: "Test question?" } });
    fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

    await waitFor(() => {
      expect(screen.getByText("Service unavailable")).toBeInTheDocument();
    });
  });

  it("sends the configured top_k value", async () => {
    const fetchSpy = mockFetch(
      new Response(JSON.stringify(sufficientAnswer), { status: 200 }),
    );
    render(<AskClient />);

    const textarea = screen.getByLabelText("Research question");
    const topKInput = screen.getByLabelText("Passages to retrieve");

    fireEvent.change(textarea, { target: { value: "Test question?" } });
    fireEvent.change(topKInput, { target: { value: "12" } });
    fireEvent.click(screen.getByRole("button", { name: "Ask question" }));

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(
        "/api/ask",
        expect.objectContaining({
          method: "POST",
          body: expect.stringContaining('"top_k":12'),
        }),
      );
    });
  });
});
