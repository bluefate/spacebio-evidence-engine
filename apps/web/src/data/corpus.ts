export type CorpusPublication = {
  id: string;
  title: string;
  doi: string;
  year: string;
  license: string;
  organism: string;
  exposure: string;
  sourceUrl: string;
  pdfUrl: string;
  notes: string;
  approval: string;
  ingestion: string;
  sections?: string[];
  chunks?: unknown[];
};

export function formatLicense(license: string): string {
  return license.toUpperCase().replaceAll("-", " ");
}

export function formatLabel(value: string): string {
  return value.replaceAll("_", " ");
}
