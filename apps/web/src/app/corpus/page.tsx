import Image from "next/image";
import Link from "next/link";

import corpus from "@/data/corpus.json";
import type { CorpusPublication } from "@/data/corpus";

import styles from "./corpus.module.css";

const publications = corpus as CorpusPublication[];

function formatLicense(license: string): string {
  return license.toUpperCase().replaceAll("-", " ");
}

function formatLabel(value: string): string {
  return value.replaceAll("_", " ");
}

export default function CorpusPage() {
  const byCount = publications.filter((item) => item.license === "cc-by").length;
  const ncndCount = publications.length - byCount;

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <Link href="/" className={styles.brand}>
          <Image
            src="/brand/logo-wordmark.png"
            alt="Space Biology Evidence Engine"
            width={280}
            height={80}
            className={styles.wordmark}
            priority
          />
        </Link>
        <h1 className={styles.heading}>Corpus</h1>
        <p className={styles.lede}>
          Metadata for the proposed August MVP corpus (microgravity and skeletal
          muscle). This app does not host publication PDFs or full text — open
          the DOI for the publisher copy.
        </p>
        <div className={styles.stats}>
          <span>{publications.length} publications</span>
          <span>{byCount} CC BY</span>
          <span>{ncndCount} CC BY-NC-ND</span>
          <span>DOI links only</span>
        </div>
      </header>

      <ol className={styles.list}>
        {publications.map((pub) => (
          <li key={pub.id} className={styles.item}>
            <div className={styles.meta}>
              <span className={styles.id}>{pub.id}</span>
              <span className={styles.year}>{pub.year}</span>
              <span className={styles.license}>{formatLicense(pub.license)}</span>
            </div>
            <h2 className={styles.title}>{pub.title}</h2>
            <p className={styles.details}>
              <span>{formatLabel(pub.organism)}</span>
              <span aria-hidden>·</span>
              <span>{formatLabel(pub.exposure)}</span>
            </p>
            <p className={styles.notes}>{pub.notes}</p>
            <div className={styles.links}>
              <a href={pub.sourceUrl} target="_blank" rel="noreferrer">
                View at DOI
              </a>
              <span className={styles.status}>
                {pub.approval} · {formatLabel(pub.ingestion)}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </main>
  );
}
