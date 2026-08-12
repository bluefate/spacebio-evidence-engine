import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AnswerEvidenceView } from "./AnswerEvidenceView";
import { CitationLinkedText } from "./CitationLinkedText";
import { splitAnswerCitationMarkers } from "./citationMarkers";

afterEach(() => {
  cleanup();
});

const passages = [
  {
    citationId: "C1",
    chunkId: "chk_soleus",
    publicationId: "pub_muscle",
    title: "Microgravity and soleus atrophy",
    section: "Results",
    page: 4,
    passageText: "Soleus muscle mass declined after unloading in flight mice.",
  },
  {
    citationId: "C2",
    chunkId: "chk_methods",
    publicationId: "pub_missing",
    title: "Missing publication fixture",
    section: "Methods",
    page: 2,
    passageText: "Animals were housed in flight cages.",
  },
] as const;

describe("splitAnswerCitationMarkers", () => {
  it("keeps surrounding prose and citation ids", () => {
    expect(splitAnswerCitationMarkers("Soleus atrophy [C1] exceeded cage controls [C2].")).toEqual([
      { kind: "text", value: "Soleus atrophy " },
      { kind: "citation", citationId: "C1", raw: "[C1]" },
      { kind: "text", value: " exceeded cage controls " },
      { kind: "citation", citationId: "C2", raw: "[C2]" },
      { kind: "text", value: "." },
    ]);
  });
});

describe("CitationLinkedText", () => {
  it("invokes onSelectCitation when a known marker is clicked", () => {
    const onSelectCitation = vi.fn();
    render(
      <CitationLinkedText
        text="Finding [C1] is supported."
        onSelectCitation={onSelectCitation}
        resolveCitation={(id) =>
          id === "C1"
            ? { known: true, publicationId: "pub_muscle", publicationAvailable: true }
            : { known: false }
        }
      />,
    );

    fireEvent.click(screen.getByTestId("citation-marker-C1"));
    expect(onSelectCitation).toHaveBeenCalledWith("C1");
    expect(screen.getByTestId("citation-publication-C1")).toHaveAttribute(
      "href",
      "/publications/pub_muscle",
    );
  });

  it("renders broken markers and broken publication links without navigation", () => {
    render(
      <CitationLinkedText
        text="Bad [C9] and known [C2]."
        resolveCitation={(id) => {
          if (id === "C2") {
            return {
              known: true,
              publicationId: "pub_missing",
              publicationAvailable: false,
            };
          }
          return { known: false };
        }}
      />,
    );

    expect(screen.getByTestId("citation-marker-broken-C9")).toBeTruthy();
    expect(screen.queryByTestId("citation-marker-C9")).toBeNull();
    expect(screen.getByTestId("citation-publication-broken-C2")).toHaveTextContent(
      "Publication unavailable",
    );
    expect(screen.queryByTestId("citation-publication-C2")).toBeNull();
  });
});

describe("AnswerEvidenceView", () => {
  it("focuses the matching evidence passage when an answer citation is clicked", () => {
    render(
      <AnswerEvidenceView
        answerText="Soleus atrophy increased in flight [C1]."
        passages={passages}
        knownPublicationIds={["pub_muscle"]}
      />,
    );

    expect(screen.getByTestId("evidence-item-C1")).toHaveAttribute("data-active", "false");
    fireEvent.click(screen.getByTestId("citation-marker-C1"));
    expect(screen.getByTestId("evidence-item-C1")).toHaveAttribute("data-active", "true");
    expect(screen.getByTestId("citation-marker-C1")).toHaveAttribute("aria-pressed", "true");
  });

  it("handles missing citations and unavailable publications", () => {
    render(
      <AnswerEvidenceView
        answerText="Unsupported [C9] versus available [C2]."
        passages={passages}
        knownPublicationIds={["pub_muscle"]}
      />,
    );

    expect(screen.getByTestId("citation-marker-broken-C9")).toBeTruthy();
    expect(screen.getByTestId("citation-publication-broken-C2")).toBeTruthy();
    expect(screen.getByTestId("evidence-publication-broken-C2")).toHaveTextContent(
      "unavailable",
    );
    expect(screen.getByTestId("evidence-publication-C1")).toHaveAttribute(
      "href",
      "/publications/pub_muscle",
    );
  });
});
