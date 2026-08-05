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

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Year</th>
              <th scope="col">Title</th>
              <th scope="col">Model</th>
              <th scope="col">Exposure</th>
              <th scope="col">License</th>
              <th scope="col">Status</th>
              <th scope="col">DOI</th>
            </tr>
          </thead>
          <tbody>
            {publications.map((pub) => (
              <tr key={pub.id}>
                <td className={styles.idCell}>{pub.id}</td>
                <td>{pub.year}</td>
                <td className={styles.titleCell}>
                  <span className={styles.title}>{pub.title}</span>
                  <span className={styles.notes}>{pub.notes}</span>
                </td>
                <td>{formatLabel(pub.organism)}</td>
                <td>{formatLabel(pub.exposure)}</td>
                <td className={styles.licenseCell}>{formatLicense(pub.license)}</td>
                <td className={styles.statusCell}>
                  {pub.approval}
                  <span className={styles.statusSub}>
                    {formatLabel(pub.ingestion)}
                  </span>
                </td>
                <td>
                  <a href={pub.sourceUrl} target="_blank" rel="noreferrer">
                    Open
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
