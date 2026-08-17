import Image from "next/image";

import { isRetrievalDiagnosticsEnabled } from "@/config/devFlags";

import styles from "./page.module.css";

export default function HomePage() {
  return (
    <main className={styles.hero}>
      <Image
        src="/brand/hero-atmosphere.png"
        alt=""
        fill
        priority
        className={styles.heroImage}
        sizes="100vw"
      />
      <section className={styles.content}>
        <Image
          src="/brand/logo-wordmark.png"
          alt="Space Biology Evidence Engine"
          width={420}
          height={120}
          className={styles.wordmark}
          priority
        />
        <p className={styles.tagline}>
          Citation-first answers from a controlled corpus of space biology
          publications.
        </p>
        <div className={styles.actions}>
          <a className={styles.primary} href="/ask">
            Ask a question
          </a>
          <a className={styles.secondary} href="/search">
            Search corpus
          </a>
          <a className={styles.secondary} href="/corpus">
            View corpus
          </a>
          {isRetrievalDiagnosticsEnabled() ? (
            <a className={styles.secondary} href="/dev/retrieval">
              Retrieval diagnostics
            </a>
          ) : null}
        </div>
      </section>
    </main>
  );
}
