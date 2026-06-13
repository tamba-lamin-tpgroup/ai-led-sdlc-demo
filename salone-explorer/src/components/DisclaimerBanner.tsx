// Dismissible disclaimer alert — persists dismiss state in localStorage.
import { useState } from "react";
import { X } from "lucide-react";
import { t } from "@/lib/content";

const STORAGE_KEY = "salone-explorer:disclaimer-dismissed";

export default function DisclaimerBanner() {
  const [dismissed, setDismissed] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === "true";
    } catch {
      return false;
    }
  });

  if (dismissed) return null;

  function handleDismiss() {
    setDismissed(true);
    try {
      localStorage.setItem(STORAGE_KEY, "true");
    } catch {
      // Storage unavailable — dismiss for this session only.
    }
  }

  return (
    <div
      role="alert"
      aria-live="polite"
      className="bg-brand-sand border-b border-warning/30"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-3 flex items-start gap-3">
        <p className="flex-1 text-sm text-text">
          <span className="font-semibold text-warning">Demo only. </span>
          {t("disclaimer.short")}
        </p>
        <button
          type="button"
          onClick={handleDismiss}
          aria-label={t("disclaimer.dismiss")}
          className="flex-shrink-0 rounded p-1 text-text-muted hover:text-text hover:bg-black/5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent"
        >
          <X size={16} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
