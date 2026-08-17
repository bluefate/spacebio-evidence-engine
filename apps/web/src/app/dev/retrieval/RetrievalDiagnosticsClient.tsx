"use client";

import { FormEvent, useState } from "react";

import {
  fetchRetrievalDiagnostics,
  type RetrievalDiagnosticsResponse,
} from "@/data/retrievalDiagnostics";

import styles from "../../ask/ask.module.css";
import localStyles from "./diagnostics.module.css";

export function RetrievalDiagnosticsClient() {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(8);
  const [response, setResponse] = useState<RetrievalDiagnosticsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = question.trim();
    setError(null);
    setResponse(null);
    if (!trimmed) {
      setError("Enter a research question to inspect retrieval.");
      return;
    }
    setLoading(true);
    const result = await fetchRetrievalDiagnostics({ question: trimmed, top_k: topK });
    if (result.error) {
      setError(result.error.message);
    } else if (result.response) {
      setResponse(result.response);
    }
    setLoading(false);
  }

  return (
    <section className={styles.askPanel} aria-labelledby="diagnostics-heading">
      <div className={styles.panelHeader}>
        <h2 id="diagnostics-heading">Retrieval probe</h2>
        <p className={styles.helpText}>
          Developer-only view of hashed query metadata, selected chunk IDs, ranks, scores, and
          citation IDs. Raw questions, passage text, prompts, and API keys are not returned.
        </p>
      </div>

      <form className={styles.askForm} onSubmit={onSubmit}>
        <label className={styles.label} htmlFor="diagnostics-question">
          Research question
        </label>
        <textarea
          id="diagnostics-question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="How does microgravity affect skeletal muscle proteome changes in astronauts?"
          className={styles.textarea}
          rows={3}
        />
        <div className={styles.topKRow}>
          <label className={styles.label} htmlFor="diagnostics-top-k">
            Passages to retrieve
          </label>
          <input
            id="diagnostics-top-k"
            type="number"
            min={1}
            max={50}
            value={topK}
            onChange={(event) => setTopK(Number(event.target.value))}
            className={styles.topKInput}
          />
        </div>
        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? "Inspecting" : "Inspect retrieval"}
        </button>
      </form>

      <div className={styles.stateLine} aria-live="polite">
        {loading && "Running retrieval diagnostics."}
        {!loading && error}
      </div>

      {response && (
        <div className={localStyles.results}>
          <dl className={localStyles.meta}>
            <div>
              <dt>Query hash</dt>
              <dd>
                <code>{response.query_sha256}</code>
              </dd>
            </div>
            <div>
              <dt>Query length</dt>
              <dd>{response.query_length}</dd>
            </div>
            <div>
              <dt>Algorithm</dt>
              <dd>
                {response.search_algorithm} ({response.score_kind})
              </dd>
            </div>
            <div>
              <dt>Embedding</dt>
              <dd>
                {response.embedding_model} · dim {response.embedding_dimension}
              </dd>
            </div>
            <div>
              <dt>Selected citations</dt>
              <dd>{response.selected_citation_ids.join(", ") || "none"}</dd>
            </div>
          </dl>

          <table className={localStyles.table}>
            <caption>Selected chunks</caption>
            <thead>
              <tr>
                <th scope="col">Citation</th>
                <th scope="col">Rank</th>
                <th scope="col">Chunk ID</th>
                <th scope="col">Score</th>
                <th scope="col">Publication</th>
                <th scope="col">Section</th>
                <th scope="col">Pages</th>
              </tr>
            </thead>
            <tbody>
              {response.selected_chunks.map((chunk) => (
                <tr key={chunk.chunk_id}>
                  <td>{chunk.citation_id}</td>
                  <td>{chunk.rank}</td>
                  <td>
                    <code>{chunk.chunk_id}</code>
                  </td>
                  <td>{chunk.score.toFixed(4)}</td>
                  <td>
                    <code>{chunk.publication_id}</code>
                  </td>
                  <td>{chunk.section}</td>
                  <td>
                    {chunk.page_start ?? "—"}
                    {chunk.page_end != null && chunk.page_end !== chunk.page_start
                      ? `–${chunk.page_end}`
                      : ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
