import { askDemoHref, DEMO_ASK_QUESTIONS, DEMO_SEARCH_TERMS, searchDemoHref } from "@/data/demo";

import styles from "./page.module.css";

export function HomeDemoLinks() {
  return (
    <section className={styles.demo} aria-labelledby="demo-heading">
      <h2 id="demo-heading" className={styles.demoHeading}>
        Demo links
      </h2>
      <p className={styles.demoLede}>
        Search terms open catalog (and passages after ingest). Ask questions
        prefill the form — submit there. Index is a separate step after you
        register a DOI or PDF.
      </p>
      <p className={styles.demoLede}>
        <a className={styles.demoInline} href="/add">
          Add paper
        </a>
        {" · "}
        <a className={styles.demoInline} href="/add#index-controls">
          Index a registered paper
        </a>
      </p>
      <div className={styles.demoColumns}>
        <div>
          <h3 className={styles.demoSubheading} id="demo-search-heading">
            Search terms
          </h3>
          <ul className={styles.demoList} aria-labelledby="demo-search-heading">
            {DEMO_SEARCH_TERMS.map((term) => (
              <li key={term}>
                <a className={styles.demoLink} href={searchDemoHref(term)}>
                  {term}
                </a>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className={styles.demoSubheading} id="demo-ask-heading">
            Ask questions
          </h3>
          <ul className={styles.demoList} aria-labelledby="demo-ask-heading">
            {DEMO_ASK_QUESTIONS.map((item) => (
              <li key={item.id}>
                <a className={styles.demoLink} href={askDemoHref(item.question)}>
                  {item.id}: {item.question}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
