import { describe, expect, it } from "vitest";

import {
  buildComparison,
  fieldValuesDiffer,
  organismSystemCategory,
  publicationsByIds,
} from "@/data/compare";
import type { CorpusPublication } from "@/data/corpus";

function pub(overrides: Partial<CorpusPublication> & Pick<CorpusPublication, "id" | "organism">): CorpusPublication {
  return {
    title: overrides.title ?? overrides.id,
    doi: "10.0/test",
    year: "2024",
    license: "cc-by",
    exposure: "spaceflight",
    sourceUrl: "https://doi.org/10.0/test",
    pdfUrl: "https://example.test/paper.pdf",
    notes: "inventory note",
    approval: "pending",
    ingestion: "not_ingested",
    ...overrides,
  };
}

describe("organism / system labels", () => {
  it("keeps human and rodent categories distinct", () => {
    expect(organismSystemCategory("human")).toBe("Human");
    expect(organismSystemCategory("mouse")).toBe("Rodent");
    expect(organismSystemCategory("engineered_tissue")).toBe("Engineered tissue");
    expect(organismSystemCategory("multi")).toBe("Mixed species — do not merge");
  });

  it("does not invent a category for unknown organism codes", () => {
    expect(organismSystemCategory("zebrafish")).toBe("zebrafish");
  });
});

describe("buildComparison", () => {
  it("flags organism differences that exist in inventory metadata", () => {
    const rows = buildComparison([
      pub({ id: "pub_a", organism: "human" }),
      pub({ id: "pub_b", organism: "mouse" }),
    ]);
    const organism = rows.find((row) => row.field === "organism");
    const system = rows.find((row) => row.field === "organismSystem");
    expect(organism?.differs).toBe(true);
    expect(system?.values).toEqual(["Human", "Rodent"]);
    expect(system?.differs).toBe(true);
  });

  it("does not invent an organism difference when inventory values match", () => {
    const rows = buildComparison([
      pub({ id: "pub_a", organism: "mouse", notes: "telomere length" }),
      pub({ id: "pub_b", organism: "mouse", notes: "myeloid infiltration" }),
    ]);
    const organism = rows.find((row) => row.field === "organism");
    const system = rows.find((row) => row.field === "organismSystem");
    expect(organism?.differs).toBe(false);
    expect(system?.differs).toBe(false);
    expect(rows.map((row) => row.label).join(" ")).not.toMatch(/finding/i);
    expect(fieldValuesDiffer(["mouse", "mouse"])).toBe(false);
  });

  it("omits unknown publication ids instead of fabricating rows", () => {
    const catalog = [pub({ id: "pub_a", organism: "human" })];
    expect(publicationsByIds(catalog, ["pub_a", "pub_missing"]).map((item) => item.id)).toEqual([
      "pub_a",
    ]);
  });
});
