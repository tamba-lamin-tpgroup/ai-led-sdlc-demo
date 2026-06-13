// Sign-up page — email/password account creation. Phase 6 adds Supabase auth.
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import SeoHead from "@/components/SeoHead";
import { t } from "@/lib/content";
import { Link } from "react-router-dom";

const SITE_URL = import.meta.env.VITE_SITE_URL ?? "https://slint-ai-sldc-demo.tpgroupsl.com";

export default function SignUpPage() {
  return (
    <>
      <SeoHead
        title={t("auth.signUp.title")}
        description={t("auth.signUp.subtitle")}
        canonical={`${SITE_URL}/signup`}
      />
      <div className="min-h-screen flex flex-col">
        <NavBar />
        <main id="main-content" tabIndex={-1} className="flex-1 flex items-center justify-center px-4 py-16">
          <div className="w-full max-w-sm">
            <h1 className="font-display text-3xl font-bold text-text mb-2">{t("auth.signUp.title")}</h1>
            <p className="text-text-muted mb-8">{t("auth.signUp.subtitle")}</p>

            <form aria-label={t("auth.signUp.title")} className="space-y-4">
              <div>
                <label htmlFor="signup-email" className="block text-sm font-medium text-text mb-1">
                  {t("auth.signUp.email")}
                </label>
                <input
                  id="signup-email"
                  type="email"
                  autoComplete="email"
                  required
                  className="w-full rounded-lg border border-border px-4 py-2.5 text-sm text-text placeholder-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent"
                  placeholder="you@example.com"
                />
              </div>
              <div>
                <label htmlFor="signup-password" className="block text-sm font-medium text-text mb-1">
                  {t("auth.signUp.password")}
                </label>
                <input
                  id="signup-password"
                  type="password"
                  autoComplete="new-password"
                  required
                  className="w-full rounded-lg border border-border px-4 py-2.5 text-sm text-text placeholder-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent"
                />
              </div>
              <button
                type="submit"
                className="w-full rounded-full bg-brand-primary px-6 py-2.5 text-sm font-semibold text-white hover:bg-brand-primary/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent min-h-[44px]"
              >
                {t("auth.signUp.cta")}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-text-muted">
              {t("auth.signUp.hasAccount")}{" "}
              <Link to="/signin" className="text-brand-accent underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded">
                {t("auth.signUp.signIn")}
              </Link>
            </p>
          </div>
        </main>
        <Footer />
      </div>
    </>
  );
}
