// Utility helpers — class merging and formatting.
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRating(rating: number): string {
  return rating.toFixed(1);
}

export function buildMapsUrl(lat: number, lng: number, name: string): string {
  const query = encodeURIComponent(`${name}, Sierra Leone`);
  return `https://www.google.com/maps/search/?api=1&query=${query}&query_place=${lat},${lng}`;
}
