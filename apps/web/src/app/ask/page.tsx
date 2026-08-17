import Image from "next/image";
import Link from "next/link";

import { AskClient } from "./AskClient";
import styles from "./ask.module.css";

export default function AskPage() {
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
        <h1 className={styles.heading}>Ask a question</h1>
        <p className={styles.lede}>
          Submit a research question and receive a grounded answer drawn from the
          controlled corpus. Every claim should link to cited passages with publication,
          section, and page provenance.
        </p>
      </header>

      <AskClient />
    </main>
  );
}
