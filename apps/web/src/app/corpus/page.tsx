import Image from "next/image";
import Link from "next/link";

import corpus from "@/data/corpus.json";
import {
  formatLabel,
  formatLicense,
  type CorpusPublication,
} from "@/data/corpus";

import styles from "./corpus.module.css";

const publications = corpus as CorpusPublication[];

function Badge({
  children,
  tone = "default",
}: {
  children: React.ReactNode;
  tone?: "default" | "accent" | "license" | "status";
}) {
  return <span className={`${styles.badge} ${styles[tone]}`}>{children}</span>;
}

export default function CorpusPage() {
  const byCount = publications.filter((item) => item.license === "cc-by").length;
  const ncndCount = publications.length - byCount;

  return (
    <main id="main-content" className={styles.page} tabIndex={-1}>
      <div className={styles.heroBackdrop} aria-hidden>
        <Image
          src="/brand/hero-atmosphere.png"
          alt=""
          fill
          priority
          className={styles.heroImage}
          sizes="100vw"
        />
      </div>
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
          <Badge tone="accent">{publications.length} publications</Badge>
          <Badge>{byCount} CC BY</Badge>
          <Badge>{ncndCount} CC BY-NC-ND</Badge>
          <Badge>DOI links only</Badge>
        </div>
      </header>

      <div className={styles.grid}>
        {publications.map((pub) => (
          <article key={pub.id} className={styles.card}>
            <div className={styles.badges}>
              <Badge tone="accent">{pub.id}</Badge>
              <Badge>{pub.year}</Badge>
              <Badge tone="license">{formatLicense(pub.license)}</Badge>
              <Badge tone="status">{pub.approval}</Badge>
            </div>
            <h2 className={styles.title}>{pub.title}</h2>
            <div className={styles.badges}>
              <Badge>{formatLabel(pub.organism)}</Badge>
              <Badge>{formatLabel(pub.exposure)}</Badge>
              <Badge>{formatLabel(pub.ingestion)}</Badge>
            </div>
            <p className={styles.notes}>{pub.notes}</p>
            <div className={styles.actions}>
              <Link className={styles.detailLink} href={`/publications/${pub.id}`}>
                Publication details
              </Link>
              <a
                className={styles.doi}
                href={pub.sourceUrl}
                target="_blank"
                rel="noreferrer"
              >
                View at DOI
              </a>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}
