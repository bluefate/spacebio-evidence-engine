import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HomeDemoLinks } from "@/app/HomeDemoLinks";
import { AddPaperClient } from "@/app/add/AddPaperClient";
import { AskClient } from "@/app/ask/AskClient";
import { CompareClient } from "@/app/compare/CompareClient";
import { SearchClient } from "@/app/search/SearchClient";
import { CitationLinkedText } from "@/components/evidence/CitationLinkedText";
import { EvidencePanel } from "@/components/evidence/EvidencePanel";
import { expectNoAxeViolations } from "@/test/axe";

import { NewTabLink } from "./NewTabLink";

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(),
}));

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("core flow accessibility", () => {
  it("exposes a skip link that targets main content", async () => {
    const user = userEvent.setup();
    render(
      <>
        <a className="skipLink" href="#main-content">
          Skip to main content
        </a>
        <main id="main-content" tabIndex={-1}>
          <SearchClient />
        </main>
      </>,
    );

    await user.tab();
    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveFocus();
    expect(document.getElementById("main-content")).toBeTruthy();
  });

  it("labels search controls and supports keyboard focus", async () => {
    const user = userEvent.setup();
    const { container } = render(<SearchClient />);

    const query = screen.getByLabelText("Query");
    expect(query).toHaveAttribute("type", "search");
    query.focus();
    await user.keyboard("microgravity");
    expect(query).toHaveValue("microgravity");
    await expectNoAxeViolations(container);
  });

  it("labels the ask form and has no axe violations on the empty state", async () => {
    const { container } = render(<AskClient />);
    expect(screen.getByLabelText("Research question")).toBeTruthy();
    expect(screen.getByLabelText("Passages to retrieve")).toBeTruthy();
    await expectNoAxeViolations(container);
  });

  it("labels citation markers and evidence selection", async () => {
    const { container } = render(
      <div>
        <CitationLinkedText
          text="Finding [C1] is supported."
          resolveCitation={() => ({
            known: true,
            publicationId: "pub_muscle",
            publicationAvailable: true,
          })}
        />
        <EvidencePanel
          passages={[
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
          ]}
          activeCitationId="C1"
          onSelectCitation={() => undefined}
        />
      </div>,
    );

    expect(screen.getByRole("button", { name: "Show evidence for citation C1" })).toBeTruthy();
    expect(screen.getByRole("link", { name: "Publication pub_muscle" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Citation C1 is active" })).toBeTruthy();
    await expectNoAxeViolations(container);
  });

  it("announces new-tab destinations", () => {
    render(<NewTabLink href="https://doi.org/10.0/example">Source</NewTabLink>);
    const link = screen.getByRole("link", { name: /Source \(opens in a new tab\)/ });
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("labels home demo search and ask links", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          catalog_count: 23,
          on_disk_count: 0,
          missing_count: 23,
          missing: ["pub_001"],
        }),
      }),
    );
    const { container } = render(<HomeDemoLinks />);
    expect(screen.getByRole("heading", { name: "Demo links" })).toBeTruthy();
    expect(screen.getByRole("link", { name: "hindlimb unloading" })).toHaveAttribute(
      "href",
      "/search?q=hindlimb%20unloading",
    );
    expect(screen.getByRole("link", { name: "Index a registered paper" })).toHaveAttribute(
      "href",
      "/add#index-controls",
    );
    expect(await screen.findByRole("button", { name: "Download missing PDFs" })).toBeTruthy();
    await expectNoAxeViolations(container);
  });

  it("labels add-paper DOI, PDF, and Index controls", async () => {
    const { container } = render(<AddPaperClient />);
    expect(screen.getByLabelText("DOI")).toBeTruthy();
    expect(screen.getByLabelText("Title")).toBeTruthy();
    expect(screen.getByLabelText("PDF file")).toBeTruthy();
    expect(screen.getByLabelText("Publication id to index")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Register DOI" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Upload and register PDF" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Index" })).toBeTruthy();
    await expectNoAxeViolations(container);
  });

  it("labels compare publication checkboxes", async () => {
    const { container } = render(
      <CompareClient
        publications={[
          {
            id: "pub_a",
            title: "Human spaceflight muscle",
            doi: "10.0/a",
            year: "2024",
            license: "cc-by",
            organism: "human",
            exposure: "spaceflight",
            sourceUrl: "https://doi.org/10.0/a",
            pdfUrl: "https://example.test/a.pdf",
            notes: "note a",
            approval: "pending",
            ingestion: "not_ingested",
          },
        ]}
      />,
    );
    expect(screen.getByLabelText(/pub_a/i)).toHaveAttribute("type", "checkbox");
    await expectNoAxeViolations(container);
  });
});
