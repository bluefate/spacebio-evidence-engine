import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import type { CorpusPublication } from "@/data/corpus";

import { CompareClient } from "./CompareClient";

afterEach(() => {
  cleanup();
});

const fixtures: CorpusPublication[] = [
  {
    id: "pub_human",
    title: "Astronaut skeletal muscle proteome",
    doi: "10.0/human",
    year: "2024",
    license: "cc-by",
    organism: "human",
    exposure: "spaceflight",
    sourceUrl: "https://doi.org/10.0/human",
    pdfUrl: "https://example.test/human.pdf",
    notes: "astronaut skeletal muscle proteome",
    approval: "pending",
    ingestion: "not_ingested",
  },
  {
    id: "pub_mouse",
    title: "Hindlimb unloading in mice",
    doi: "10.0/mouse",
    year: "2023",
    license: "cc-by",
    organism: "mouse",
    exposure: "simulated_microgravity",
    sourceUrl: "https://doi.org/10.0/mouse",
    pdfUrl: "https://example.test/mouse.pdf",
    notes: "hindlimb unloading genetic diversity",
    approval: "pending",
    ingestion: "not_ingested",
  },
];

describe("CompareClient labeling", () => {
  it("labels organism/system categories after two publications are selected", async () => {
    const user = userEvent.setup();
    render(<CompareClient publications={fixtures} />);

    expect(
      screen.getByText(/does not retrieve passages, generate findings, or invent differences/i),
    ).toBeTruthy();
    expect(screen.getByText(/Select two or more publications/i)).toBeTruthy();

    await user.click(screen.getByLabelText(/pub_human/i));
    await user.click(screen.getByLabelText(/pub_mouse/i));

    expect(screen.getByRole("columnheader", { name: "pub_human" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "pub_mouse" })).toBeTruthy();
    expect(screen.getByRole("rowheader", { name: "Organism / system category" })).toBeTruthy();
    expect(screen.getByRole("rowheader", { name: "Organism (inventory)" })).toBeTruthy();
    expect(screen.getByText("Human")).toBeTruthy();
    expect(screen.getByText("Rodent")).toBeTruthy();
    expect(screen.queryByRole("rowheader", { name: /finding/i })).toBeNull();
  });
});
