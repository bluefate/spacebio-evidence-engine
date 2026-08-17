import { describe, expect, it } from "vitest";

import { askDemoHref, DEMO_ASK_QUESTIONS, DEMO_SEARCH_TERMS, searchDemoHref } from "./demo";

describe("demo links", () => {
  it("has ten search terms and ten questions", () => {
    expect(DEMO_SEARCH_TERMS).toHaveLength(10);
    expect(DEMO_ASK_QUESTIONS).toHaveLength(10);
  });

  it("builds search and ask query URLs", () => {
    expect(searchDemoHref("hindlimb unloading")).toBe(
      "/search?q=hindlimb%20unloading",
    );
    expect(askDemoHref("What happened?")).toBe("/ask?q=What%20happened%3F");
  });
});
