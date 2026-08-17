import { describe, expect, it } from "vitest";

import { isRetrievalDiagnosticsEnabled } from "./devFlags";

describe("isRetrievalDiagnosticsEnabled", () => {
  it("hides diagnostics by default", () => {
    expect(isRetrievalDiagnosticsEnabled({})).toBe(false);
    expect(isRetrievalDiagnosticsEnabled({ NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS: "" })).toBe(
      false,
    );
    expect(
      isRetrievalDiagnosticsEnabled({ NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS: "false" }),
    ).toBe(false);
  });

  it("enables only for explicit truthy values", () => {
    expect(
      isRetrievalDiagnosticsEnabled({ NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS: "true" }),
    ).toBe(true);
    expect(isRetrievalDiagnosticsEnabled({ NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS: "1" })).toBe(
      true,
    );
  });
});
