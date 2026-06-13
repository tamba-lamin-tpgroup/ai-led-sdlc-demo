// File-based attraction repository — reads from src/data/attractions.json.
// Active when VITE_ATTRACTIONS_SOURCE=file (the default). Per SPEC §5.2.3.
import attractionsData from "@/data/attractions.json";
import type { Attraction } from "@/data/types";
import type { AttractionRepository } from "./attractions";

export const fileAttractionRepository: AttractionRepository = {
  async getAll() {
    return attractionsData as Attraction[];
  },
  async getById(id: string) {
    return (attractionsData as Attraction[]).find((a) => a.id === id) ?? null;
  },
};
