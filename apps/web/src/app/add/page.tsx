import Image from "next/image";
import Link from "next/link";

import { AddPaperClient } from "./AddPaperClient";
import styles from "../search/search.module.css";

export default function AddPaperPage() {
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
        <h1 className={styles.heading}>Add paper</h1>
        <p className={styles.lede}>
          Register a DOI or upload a PDF as a local extra, then index. Catalog
          papers stay the approved 23 until a human says otherwise.
        </p>
      </header>
      <AddPaperClient />
    </main>
  );
}
