"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { NewTabLink } from "@/components/a11y/NewTabLink";
import type { SearchResponse } from "@/data/search";

import styles from "./search.module.css";

const emptyResponse: SearchResponse = {
  query: "",
  total: 0,
  source: "inventory",
  publications: [],
  passages: [],
};

export function SearchClient() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState<SearchResponse>(emptyResponse);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    setSearched(true);
    setError(null);

    if (!trimmed) {
      setResponse(emptyResponse);
      return;
    }

    setLoading(true);
    try {
      const result = await fetch(`/api/search?q=${encodeURIComponent(trimmed)}`, {
        headers: { Accept: "application/json" },
      });
      if (!result.ok) {
        throw new Error(`Search request failed with status ${result.status}`);
      }
      setResponse((await result.json()) as SearchResponse);
    } catch {
      setError("Search is unavailable. Check that the web app is running normally.");
      setResponse(emptyResponse);
    } finally {
      setLoading(false);
    }
  }

  const hasResults = response.total > 0;

  return (
    <section className={styles.searchPanel} aria-labelledby="search-heading">
      <div className={styles.panelHeader}>
        <h2 id="search-heading">Search Stored Corpus</h2>
        <Link href="/corpus" className={styles.secondaryLink}>
          View corpus
        </Link>
      </div>

      <form className={styles.searchForm} onSubmit={onSubmit}>
        <label className={styles.label} htmlFor="corpus-search">
          Query
        </label>
        <div className={styles.inputRow}>
          <input
            id="corpus-search"
            name="q"
            type="search"
            autoComplete="off"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="microgravity skeletal muscle"
            className={styles.input}
          />
          <button
            className={styles.button}
            type="submit"
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? "Searching" : "Search"}
          </button>
        </div>
      </form>

      <div className={styles.stateLine} aria-live="polite">
        {loading && "Loading stored corpus results."}
        {!loading && error}
        {!loading &&
          !error &&
          searched &&
          !hasResults &&
          "No stored publication or passage records matched."}
        {!loading &&
          !error &&
          hasResults &&
          `${response.total} result${response.total === 1 ? "" : "s"} for "${response.query}" (${response.source === "inventory" ? "catalog only" : response.source === "indexed" ? "indexed passages" : "catalog + indexed passages"}).`}
        {!loading && !error && !searched && "Catalog titles always search. Passages appear after ingest if the API is running."}
      </div>

      <div className={styles.resultsGrid}>
        <section className={styles.resultsColumn} aria-labelledby="publication-results">
          <h3 id="publication-results">Publications</h3>
          {response.publications.length > 0 ? (
            <div className={styles.resultList}>
              {response.publications.map((publication) => (
                <article className={styles.resultCard} key={publication.publicationId}>
                  <div className={styles.badges}>
                    <span className={`${styles.badge} ${styles.accent}`}>
                      {publication.publicationId}
                    </span>
                    <span className={styles.badge}>{publication.year}</span>
                    <span className={styles.badge}>{publication.license}</span>
                  </div>
                  <h4>{publication.title}</h4>
                  <dl className={styles.provenance}>
                    <div>
                      <dt>DOI</dt>
                      <dd>{publication.doi}</dd>
                    </div>
                    <div>
                      <dt>Organism</dt>
                      <dd>{publication.organism}</dd>
                    </div>
                    <div>
                      <dt>Exposure</dt>
                      <dd>{publication.exposure}</dd>
                    </div>
                    <div>
                      <dt>Ingestion</dt>
                      <dd>{publication.ingestion}</dd>
                    </div>
                  </dl>
                  <p>{publication.notes}</p>
                  <div className={styles.actions}>
                    <Link href={`/publications/${publication.publicationId}`}>
                      Details for {publication.publicationId}
                    </Link>
                    <NewTabLink href={publication.sourceUrl}>Source</NewTabLink>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <p className={styles.emptyState}>No publication metadata matches yet.</p>
          )}
        </section>

        <section className={styles.resultsColumn} aria-labelledby="passage-results">
          <h3 id="passage-results">Passages</h3>
          {response.passages.length > 0 ? (
            <div className={styles.resultList}>
              {response.passages.map((passage) => (
                <article className={styles.resultCard} key={passage.chunkId}>
                  <div className={styles.badges}>
                    <span className={`${styles.badge} ${styles.accent}`}>{passage.chunkId}</span>
                    <span className={styles.badge}>{passage.publicationId}</span>
                    <span className={styles.badge}>{passage.section}</span>
                  </div>
                  <h4>{passage.title}</h4>
                  <p>{passage.excerpt}</p>
                  <dl className={styles.provenance}>
                    <div>
                      <dt>Page</dt>
                      <dd>{formatPageRange(passage.pageStart, passage.pageEnd)}</dd>
                    </div>
                    <div>
                      <dt>Source</dt>
                      <dd>
                        <NewTabLink href={passage.sourceUrl}>Original publication</NewTabLink>
                      </dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          ) : (
            <p className={styles.emptyState}>
              No indexed passages yet. Catalog search still uses titles and labels. Run ingest, then
              keep the API running.
            </p>
          )}
        </section>
      </div>
    </section>
  );
}

function formatPageRange(start: number | null, end: number | null): string {
  if (start === null && end === null) {
    return "not stored";
  }
  if (start !== null && end !== null && start !== end) {
    return `${start}-${end}`;
  }
  return `${start ?? end}`;
}
