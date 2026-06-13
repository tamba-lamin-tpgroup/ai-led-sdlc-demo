// Reference data loader for authoritative data sources listed in SPEC §4.
// Pages read this through the barrel, never by importing data/ directly.
import sourcesData from "@/data/sources.json";

export type DataSource = { name: string; url: string };

export function getSources(): DataSource[] {
  return sourcesData as DataSource[];
}
