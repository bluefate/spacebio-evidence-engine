import { beforeEach, describe, expect, it, vi } from "vitest";

const notFound = vi.fn(() => {
  throw new Error("NEXT_NOT_FOUND");
});

vi.mock("next/navigation", () => ({
  notFound,
}));

vi.mock("next/image", () => ({
  default: () => null,
}));

vi.mock("./RetrievalDiagnosticsClient", () => ({
  RetrievalDiagnosticsClient: () => <div>diagnostics-client</div>,
}));

describe("RetrievalDiagnosticsPage", () => {
  beforeEach(() => {
    notFound.mockClear();
    vi.resetModules();
    vi.unstubAllEnvs();
  });

  it("calls notFound when the developer flag is unset", async () => {
    vi.stubEnv("NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS", "");
    const { default: RetrievalDiagnosticsPage } = await import("./page");
    expect(() => RetrievalDiagnosticsPage()).toThrow("NEXT_NOT_FOUND");
    expect(notFound).toHaveBeenCalled();
  });
});
