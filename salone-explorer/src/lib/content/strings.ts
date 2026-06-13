// Strings indirection — all UI copy flows through t(). Per SPEC §5.2.2.
// Never write English literals in component or page files.
import en from "@/content/strings.en.json";

type StringKey = keyof typeof en;

export function t(key: StringKey, fallback?: string): string {
  return en[key] ?? fallback ?? key;
}
