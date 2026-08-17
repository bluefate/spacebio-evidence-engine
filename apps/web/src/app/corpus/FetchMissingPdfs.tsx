"use client";

import { useEffect, useState } from "react";

type StatusPayload = {
  catalog_count?: number;
  on_disk_count?: number;
  missing_count?: number;
  missing?: string[];
  detail?: string;
};

type FetchPayload = {
  downloaded_count?: number;
  failed_count?: number;
  message?: string;
  failed?: { publication_id: string; message: string }[];
  detail?: string;
};

export function FetchMissingPdfs({ className }: { className?: string }) {
  const [status, setStatus] = useState<StatusPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  async function loadStatus() {
    try {
      const response = await fetch("/api/publications/catalog-pdfs/status");
      const payload = (await response.json()) as StatusPayload;
      if (!response.ok) {
        setError(typeof payload.detail === "string" ? payload.detail : "Status request failed.");
        return;
      }
      setError(null);
      setStatus(payload);
    } catch {
      setError("Could not reach the API. Start `make api` in this repo.");
    }
  }

  useEffect(() => {
    void loadStatus();
  }, []);

  async function onDownload() {
    setBusy(true);
    setError(null);
    setNote(null);
    try {
      const response = await fetch("/api/publications/catalog-pdfs/fetch-missing", {
        method: "POST",
      });
      const payload = (await response.json()) as FetchPayload;
      if (!response.ok) {
        setError(typeof payload.detail === "string" ? payload.detail : "Download failed.");
        return;
      }
      setNote(
        `${payload.message ?? "Download finished."}` +
          (payload.failed_count
            ? ` Failed: ${(payload.failed ?? []).map((item) => item.publication_id).join(", ")}`
            : ""),
      );
      await loadStatus();
    } catch {
      setError("Could not reach the API.");
    } finally {
      setBusy(false);
    }
  }

  const missing = status?.missing_count ?? null;

  return (
    <div className={className}>
      <p>
        Catalog lists {status?.catalog_count ?? "23"} approved papers. On disk:{" "}
        {status?.on_disk_count ?? "…"}. Missing: {missing ?? "…"}.
        Download does not index; run ingest after files land.
      </p>
      <button type="button" onClick={onDownload} disabled={busy || missing === 0}>
        {busy ? "Downloading missing PDFs…" : "Download missing PDFs"}
      </button>
      {error ? <p role="alert">{error}</p> : null}
      {note ? <p>{note}</p> : null}
    </div>
  );
}
