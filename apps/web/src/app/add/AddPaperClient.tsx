"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import styles from "../search/search.module.css";

type RegisterPayload = {
  publication_id?: string;
  title?: string;
  pdf_stored?: boolean;
  human_approval?: string;
  collection?: string;
  detail?: string;
};

type IndexPayload = {
  publication_id?: string;
  ingestion_status?: string;
  chunk_count?: number;
  message?: string | null;
  detail?: string;
};

function detailMessage(payload: { detail?: unknown }): string {
  if (typeof payload.detail === "string") {
    return payload.detail;
  }
  if (Array.isArray(payload.detail)) {
    return payload.detail
      .map((item) =>
        typeof item === "object" && item && "msg" in item
          ? String((item as { msg: string }).msg)
          : String(item),
      )
      .join(" ");
  }
  return "Request failed.";
}

export function AddPaperClient() {
  const [doi, setDoi] = useState("");
  const [title, setTitle] = useState("");
  const [licenseId, setLicenseId] = useState("cc-by");
  const [organism, setOrganism] = useState("");
  const [exposure, setExposure] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [lastId, setLastId] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onDoi(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setStatus(null);
    try {
      const response = await fetch("/api/publications/from-doi", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          doi: doi.trim(),
          organism_model: organism.trim() || null,
          exposure: exposure.trim() || null,
        }),
      });
      const payload = (await response.json()) as RegisterPayload;
      if (!response.ok) {
        setError(detailMessage(payload));
        return;
      }
      setLastId(payload.publication_id ?? "");
      setStatus(
        `Registered ${payload.publication_id} (${payload.collection}). PDF stored: ${payload.pdf_stored ? "yes" : "no"}. Approval: ${payload.human_approval}. This is a local extra, not one of the 23 catalog papers.`,
      );
    } catch {
      setError("Could not reach the web API route.");
    } finally {
      setBusy(false);
    }
  }

  async function onPdf(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose a PDF file.");
      return;
    }
    setBusy(true);
    setError(null);
    setStatus(null);
    const form = new FormData();
    form.set("title", title.trim());
    form.set("license_id", licenseId);
    if (doi.trim()) {
      form.set("doi", doi.trim());
    }
    if (organism.trim()) {
      form.set("organism_model", organism.trim());
    }
    if (exposure.trim()) {
      form.set("exposure", exposure.trim());
    }
    form.set("file", file);
    try {
      const response = await fetch("/api/publications/from-pdf", {
        method: "POST",
        body: form,
      });
      const payload = (await response.json()) as RegisterPayload;
      if (!response.ok) {
        setError(detailMessage(payload));
        return;
      }
      setLastId(payload.publication_id ?? "");
      setStatus(
        `Registered ${payload.publication_id}. PDF stored: ${payload.pdf_stored ? "yes" : "no"}. Not indexed until you click Index.`,
      );
    } catch {
      setError("Could not reach the web API route.");
    } finally {
      setBusy(false);
    }
  }

  async function onIndex() {
    if (!lastId) {
      setError("Register a paper first, or paste a local_* id.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/publications/${encodeURIComponent(lastId)}/index`,
        { method: "POST" },
      );
      const payload = (await response.json()) as IndexPayload;
      if (!response.ok) {
        setError(detailMessage(payload));
        return;
      }
      setStatus(
        `Index ${payload.ingestion_status ?? "unknown"} for ${payload.publication_id}: ${payload.chunk_count ?? 0} chunks. This does not train a model.`,
      );
    } catch {
      setError("Could not reach the web API route.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.searchPanel} aria-labelledby="add-paper-heading">
      <div className={styles.panelHeader}>
        <h2 id="add-paper-heading">Add a local extra</h2>
        <Link href="/corpus" className={styles.secondaryLink}>
          View corpus
        </Link>
      </div>
      <p>
        These papers go into a <strong>local extras</strong> collection (
        <code>local_*</code>), pending review. They are not added to the approved 23.
        Paywalled licenses are rejected. Index only extracts and embeds; it does not
        train.
      </p>

      <div className={styles.stateLine} aria-live="polite">
        {busy && "Working."}
        {!busy && error}
        {!busy && !error && status}
      </div>

      <form className={styles.searchForm} onSubmit={onDoi}>
        <label className={styles.label} htmlFor="add-doi">
          DOI
        </label>
        <div className={styles.inputRow}>
          <input
            id="add-doi"
            name="doi"
            type="text"
            autoComplete="off"
            value={doi}
            onChange={(event) => setDoi(event.target.value)}
            placeholder="10.1038/s41526-024-00406-3"
            className={styles.input}
          />
          <button className={styles.button} type="submit" disabled={busy}>
            Register DOI
          </button>
        </div>
      </form>

      <form className={styles.searchForm} onSubmit={onPdf}>
        <label className={styles.label} htmlFor="add-title">
          Title
        </label>
        <input
          id="add-title"
          name="title"
          type="text"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className={styles.input}
          required
        />
        <label className={styles.label} htmlFor="add-license">
          License
        </label>
        <select
          id="add-license"
          name="license_id"
          value={licenseId}
          onChange={(event) => setLicenseId(event.target.value)}
          className={styles.input}
        >
          <option value="cc-by">CC BY</option>
          <option value="cc-by-nc-nd">CC BY-NC-ND</option>
          <option value="unknown">Unknown (needs review, no auto-download)</option>
        </select>
        <label className={styles.label} htmlFor="add-organism">
          Organism / model (optional)
        </label>
        <input
          id="add-organism"
          name="organism_model"
          type="text"
          value={organism}
          onChange={(event) => setOrganism(event.target.value)}
          className={styles.input}
          placeholder="human, mouse, engineered_tissue"
        />
        <label className={styles.label} htmlFor="add-exposure">
          Exposure (optional)
        </label>
        <input
          id="add-exposure"
          name="exposure"
          type="text"
          value={exposure}
          onChange={(event) => setExposure(event.target.value)}
          className={styles.input}
          placeholder="spaceflight, hindlimb_unloading"
        />
        <label className={styles.label} htmlFor="add-file">
          PDF file
        </label>
        <input
          id="add-file"
          name="file"
          type="file"
          accept="application/pdf,.pdf"
          className={styles.input}
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <button className={styles.button} type="submit" disabled={busy}>
          Upload and register PDF
        </button>
      </form>

      <div className={styles.inputRow} id="index-controls">
        <label className={styles.label} htmlFor="index-id">
          Publication id to index
        </label>
        <input
          id="index-id"
          name="publication_id"
          type="text"
          value={lastId}
          onChange={(event) => setLastId(event.target.value)}
          className={styles.input}
          placeholder="local_…"
        />
        <button className={styles.button} type="button" onClick={onIndex} disabled={busy}>
          Index
        </button>
      </div>
    </section>
  );
}
