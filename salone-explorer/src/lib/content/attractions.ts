// AttractionRepository interface — the contract all implementations must satisfy.
// Per SPEC §5.2.3. Never import this from components — use the barrel (index.ts).
import type { Attraction } from "@/data/types";

export interface AttractionRepository {
  getAll(): Promise<Attraction[]>;
  getById(id: string): Promise<Attraction | null>;
}
