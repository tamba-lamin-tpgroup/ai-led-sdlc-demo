// Supabase-backed attraction repository — active when VITE_ATTRACTIONS_SOURCE=supabase.
// Implements Phase 2.5 optional migration. Per SPEC §5.3.
import type { Attraction } from "@/data/types";
import type { AttractionRepository } from "./attractions";
import { cachedFetch } from "./cache";

function toAttraction(row: Record<string, unknown>): Attraction {
  return {
    id: row.id as string,
    name: row.name as string,
    shortDescription: row.short_description as string,
    longDescription: row.long_description as string,
    location: {
      region: row.region as string,
      latitude: Number(row.latitude),
      longitude: Number(row.longitude),
    },
    hours: {
      open: (row.hours_open as string) ?? "",
      close: (row.hours_close as string) ?? "",
      daysOpen: (row.hours_days as string) ?? "",
      notes: row.hours_notes as string | undefined,
    },
    rating: Number(row.rating ?? 0),
    reviewCount: Number(row.review_count ?? 0),
    images: (row.images as string[]) ?? [],
    videoUrl: row.video_url as string | undefined,
    tags: (row.tags as string[]) ?? [],
    sources: (row.sources as string[]) ?? [],
    faqs: row.faqs as Attraction["faqs"],
    lastReviewed: row.last_reviewed as string | undefined,
  };
}

async function makeClient() {
  const { createClient } = await import("@supabase/supabase-js");
  return createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY,
  );
}

export const supabaseAttractionRepository: AttractionRepository = {
  getAll() {
    return cachedFetch("attractions:all", async () => {
      const supabase = await makeClient();
      const { data, error } = await supabase.from("attractions").select("*").order("name");
      if (error) throw new Error(`attractions.getAll: ${error.message}`);
      if (!data) throw new Error("attractions.getAll: no data returned — check RLS policy for anon read");
      return (data as Record<string, unknown>[]).map(toAttraction);
    });
  },
  getById(id: string) {
    return cachedFetch(`attractions:${id}`, async () => {
      const supabase = await makeClient();
      const { data, error } = await supabase.from("attractions").select("*").eq("id", id).maybeSingle();
      if (error) throw new Error(`attractions.getById: ${error.message}`);
      return data ? toAttraction(data as Record<string, unknown>) : null;
    });
  },
};
