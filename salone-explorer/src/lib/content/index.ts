// Content barrel — selects the active attraction repository by env var.
// Components import only from this barrel; never import repositories directly.
// Per SPEC §5.2.3.
import { fileAttractionRepository } from "./attractions.file";
import { supabaseAttractionRepository } from "./attractions.supabase";

const source = import.meta.env.VITE_ATTRACTIONS_SOURCE ?? "file";

export const attractions =
  source === "supabase" ? supabaseAttractionRepository : fileAttractionRepository;

export { t } from "./strings";
export { getSources } from "./sources";
export type { AttractionRepository } from "./attractions";
export type { DataSource } from "./sources";
