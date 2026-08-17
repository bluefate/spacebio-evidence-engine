import { formatLabel, formatLicense, type CorpusPublication } from "@/data/corpus";

/** Inventory organism codes → system category. Unknown codes stay labeled, never merged. */
export const ORGANISM_SYSTEM_CATEGORIES: Readonly<Record<string, string>> = {
  human: "Human",
  mouse: "Rodent",
  rat: "Rodent",
  engineered_tissue: "Engineered tissue",
  cell_culture: "Cell culture",
  cell: "Cell culture",
  multi: "Mixed species — do not merge",
};

export type ComparisonFieldId =
  | "id"
  | "title"
  | "year"
  | "organism"
  | "organismSystem"
  | "exposure"
  | "notes"
  | "license";

export type ComparisonRow = {
  field: ComparisonFieldId;
  label: string;
  values: string[];
  differs: boolean;
};

export function organismSystemCategory(organism: string): string {
  const mapped = ORGANISM_SYSTEM_CATEGORIES[organism];
  if (mapped) {
    return mapped;
  }
  return formatLabel(organism);
}

export function fieldValuesDiffer(values: readonly string[]): boolean {
  return new Set(values).size > 1;
}

export function publicationsByIds(
  catalog: readonly CorpusPublication[],
  ids: readonly string[],
): CorpusPublication[] {
  const byId = new Map(catalog.map((item) => [item.id, item]));
  return ids.flatMap((id) => {
    const found = byId.get(id);
    return found ? [found] : [];
  });
}

export function buildComparison(selected: readonly CorpusPublication[]): ComparisonRow[] {
  if (selected.length === 0) {
    return [];
  }
  const specs: Array<{
    field: ComparisonFieldId;
    label: string;
    value: (item: CorpusPublication) => string;
  }> = [
    { field: "id", label: "Publication ID", value: (item) => item.id },
    { field: "title", label: "Title", value: (item) => item.title },
    { field: "year", label: "Year", value: (item) => item.year },
    {
      field: "organism",
      label: "Organism (inventory)",
      value: (item) => formatLabel(item.organism),
    },
    {
      field: "organismSystem",
      label: "Organism / system category",
      value: (item) => organismSystemCategory(item.organism),
    },
    {
      field: "exposure",
      label: "Exposure (inventory)",
      value: (item) => formatLabel(item.exposure),
    },
    {
      field: "notes",
      label: "Corpus inventory note",
      value: (item) => item.notes,
    },
    {
      field: "license",
      label: "License",
      value: (item) => formatLicense(item.license),
    },
  ];
  return specs.map((spec) => {
    const values = selected.map(spec.value);
    return {
      field: spec.field,
      label: spec.label,
      values,
      differs: fieldValuesDiffer(values),
    };
  });
}
