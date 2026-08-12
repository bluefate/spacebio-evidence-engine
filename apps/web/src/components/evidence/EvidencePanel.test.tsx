import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { EvidencePanel } from "./EvidencePanel";
import { toEvidencePassage } from "./types";

afterEach(() => {
  cleanup();
});

const fixtures = [
  {
    citationId: "C1",
    chunkId: "chk_soleus",
    publicationId: "pub_muscle",
    title: "Microgravity and soleus atrophy",
    section: "Results",
    page: 4,
    sourceUrl: "https://doi.org/10.0/muscle",
    passageText: "Soleus muscle mass declined after unloading in flight mice.",
  },
  {
    citation_id: "C2",
    chunk_id: "chk_methods",
    publication_id: "pub_muscle",
    title: "Microgravity and soleus atrophy",
    section: "Methods",
    page: 2,
    excerpt: "Animals were housed in flight cages under controlled lighting.",
  },
] as const;

describe("toEvidencePassage", () => {
  it("maps snake_case PassageCitation fields", () => {
    const passage = toEvidencePassage({
      citation_id: "C9",
      chunk_id: "chk_x",
      publication_id: "pub_x",
      title: "Example",
      section: "Discussion",
      page: 11,
      excerpt: "Short excerpt",
    });

    expect(passage).toEqual({
      citationId: "C9",
      chunkId: "chk_x",
      publicationId: "pub_x",
      title: "Example",
      section: "Discussion",
      page: 11,
      sourceUrl: null,
      passageText: "Short excerpt",
      excerpt: "Short excerpt",
    });
  });

  it("rejects incomplete citation rows", () => {
    expect(toEvidencePassage({ citation_id: "C1" })).toBeNull();
  });
});

describe("EvidencePanel", () => {
  it("renders passage text and provenance", () => {
    render(<EvidencePanel passages={fixtures} activeCitationId="C1" />);

    expect(screen.getByTestId("evidence-text-C1")).toHaveTextContent(
      "Soleus muscle mass declined after unloading in flight mice.",
    );
    expect(screen.getAllByText("pub_muscle").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Microgravity and soleus atrophy").length).toBeGreaterThan(0);
    expect(screen.getByText("Results")).toBeTruthy();
    expect(screen.getByText("4")).toBeTruthy();
    expect(screen.getByTestId("evidence-item-C1")).toHaveAttribute("data-active", "true");
    expect(screen.getByTestId("evidence-item-C2")).toHaveAttribute("data-active", "false");
  });

  it("highlights the active citation and supports selection", () => {
    const onSelectCitation = vi.fn();
    render(
      <EvidencePanel
        passages={fixtures}
        activeCitationId="C2"
        onSelectCitation={onSelectCitation}
      />,
    );

    expect(screen.getByTestId("evidence-item-C2")).toHaveAttribute("data-active", "true");
    fireEvent.click(screen.getByRole("button", { name: "Show citation" }));
    expect(onSelectCitation).toHaveBeenCalledWith("C1");
  });

  it("handles an empty passage list gracefully", () => {
    render(<EvidencePanel passages={[]} />);
    expect(screen.getByTestId("evidence-empty")).toHaveTextContent(
      "No cited passages are available for this answer.",
    );
  });

  it("handles a missing active citation gracefully", () => {
    render(<EvidencePanel passages={fixtures} activeCitationId="C99" />);
    expect(screen.getByTestId("evidence-missing-active")).toHaveTextContent("C99");
    expect(screen.getByTestId("evidence-item-C1")).toHaveAttribute("data-active", "false");
  });

  it("handles missing passage text and provenance fields", () => {
    render(
      <EvidencePanel
        passages={[
          {
            citationId: "C3",
            chunkId: "chk_empty",
            publicationId: "pub_unknown",
          },
        ]}
        activeCitationId="C3"
      />,
    );

    expect(screen.getByTestId("evidence-text-C3")).toHaveTextContent(
      "Passage text unavailable for this citation.",
    );
    expect(screen.getAllByText("Unknown").length).toBeGreaterThanOrEqual(2);
  });
});
