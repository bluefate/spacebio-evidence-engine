import { describe, expect, it } from "vitest";

import { mergeInventoryAndIndexedSearch, searchStoredCorpus } from "./search";

describe("mergeInventoryAndIndexedSearch", () => {
  it("keeps catalog publications and inventory source when the index is empty", () => {
    const inventory = searchStoredCorpus("microgravity", 5);
    const merged = mergeInventoryAndIndexedSearch(inventory, {
      source: "inventory_only",
      passages: [],
    });
    expect(merged.source).toBe("inventory");
    expect(merged.publications.length).toBeGreaterThan(0);
    expect(merged.passages).toEqual([]);
  });

  it("attaches indexed passages and keeps publication cards", () => {
    const inventory = searchStoredCorpus("microgravity", 5);
    const merged = mergeInventoryAndIndexedSearch(inventory, {
      source: "indexed",
      passages: [
        {
          chunk_id: "chk_1",
          publication_id: "pub_001",
          title: "Indexed title",
          section: "results",
          page_start: 2,
          page_end: 3,
          source_url: "https://doi.org/10.0/pub_001",
          excerpt: "A passage from the PDF.",
        },
      ],
    });
    expect(merged.source).toBe("mixed");
    expect(merged.passages).toHaveLength(1);
    expect(merged.passages[0]?.chunkId).toBe("chk_1");
    expect(merged.passages[0]?.pageStart).toBe(2);
    expect(merged.publications.length).toBe(inventory.publications.length);
  });
});
