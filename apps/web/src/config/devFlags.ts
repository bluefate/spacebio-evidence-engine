const TRUE_VALUES = new Set(["1", "true", "yes", "on"]);

export const RETRIEVAL_DIAGNOSTICS_ENV = "NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS";

export function isRetrievalDiagnosticsEnabled(
  env: NodeJS.ProcessEnv | Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[RETRIEVAL_DIAGNOSTICS_ENV] ?? "";
  return TRUE_VALUES.has(raw.trim().toLowerCase());
}
