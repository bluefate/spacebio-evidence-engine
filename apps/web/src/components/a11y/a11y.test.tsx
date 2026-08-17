import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import { AskClient } from "@/app/ask/AskClient";
import { SearchClient } from "@/app/search/SearchClient";
import { CitationLinkedText } from "@/components/evidence/CitationLinkedText";
import { EvidencePanel } from "@/components/evidence/EvidencePanel";
import { expectNoAxeViolations } from "@/test/axe";

import { NewTabLink } from "./NewTabLink";

afterEach(() => {
  cleanup();
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
});
