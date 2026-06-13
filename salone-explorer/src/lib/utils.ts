// Utility helpers — class merging, formatting, and URL safety validation.
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

/** Returns true only for http: and https: URLs. Rejects javascript:, data:, and protocol-relative URLs. */
export function isSafeExternalUrl(url: string): boolean {
  try {
    const { protocol } = new URL(url);
    return protocol === "https:" || protocol === "http:";
  } catch {
    return false;
  }
}

const ALLOWED_VIDEO_HOSTS = new Set(["www.youtube.com", "youtu.be", "www.youtube-nocookie.com"]);

/** Returns a sandboxed embed URL for YouTube, or null if the URL is not from an allowed host. */
export function safeYouTubeEmbedUrl(rawUrl: string): string | null {
  if (!isSafeExternalUrl(rawUrl)) return null;
  try {
    const parsed = new URL(rawUrl);
    if (!ALLOWED_VIDEO_HOSTS.has(parsed.hostname)) return null;
    // Normalise watch?v=X and youtu.be/X to embed form.
    const videoId =
      parsed.searchParams.get("v") ??
      (parsed.hostname === "youtu.be" ? parsed.pathname.slice(1) : null);
    if (!videoId || !/^[\w-]{11}$/.test(videoId)) return null;
    return `https://www.youtube-nocookie.com/embed/${videoId}?cc_load_policy=1`;
  } catch {
    return null;
  }
}
