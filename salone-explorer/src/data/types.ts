// Domain types for Salone Explorer — shared across all repository implementations.
// Canonical definition per SPEC §6.1. Do not change without updating SPEC and the Supabase schema.

export type Attraction = {
  id: string;
  name: string;
  shortDescription: string;
  longDescription: string;
  location: { region: string; latitude: number; longitude: number };
  hours: { open: string; close: string; daysOpen: string; notes?: string };
  rating: number;
  reviewCount: number;
  images: string[];
  videoUrl?: string;
  tags: string[];
  sources: string[];
  faqs?: { question: string; answer: string }[];
  lastReviewed?: string;
};

export type Region = {
  district: string;
  province: string;
};
