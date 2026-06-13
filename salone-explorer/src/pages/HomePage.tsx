// Home page — hero + attraction grid. Public route at /.
import { useEffect, useMemo, useState } from "react";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import AttractionCard from "@/components/AttractionCard";
import SeoHead from "@/components/SeoHead";
import JsonLd from "@/components/JsonLd";
import { attractions, t } from "@/lib/content";
import { buildGraph, buildWebSiteSchema } from "@/seo/graph";
import type { Attraction } from "@/data/types";

const SITE_URL = import.meta.env.VITE_SITE_URL ?? "https://slint-ai-sldc-demo.tpgroupsl.com";

export default function HomePage() {
  const [list, setList] = useState<Attraction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    attractions
      .getAll()
      .then(setList)
      .catch(() => setError(t("errors.generic")))
      .finally(() => setLoading(false));
  }, []);

  const graph = useMemo(() => buildGraph([buildWebSiteSchema()]), []);

  return (
    <>
      <SeoHead
        title={t("app.name")}
        description={t("app.tagline")}
        canonical={SITE_URL}
      />
      <JsonLd graph={graph} />

      <div className="min-h-screen flex flex-col">
        <NavBar />
        <DisclaimerBanner />

        <main id="main-content" tabIndex={-1}>
          {/* Hero */}
          <section
            aria-labelledby="hero-heading"
            className="bg-tpgroup-primary text-white py-20 px-4 sm:px-6 lg:px-8"
          >
            <div className="mx-auto max-w-4xl text-center">
              <p className="text-brand-sand font-medium text-sm uppercase tracking-widest mb-3">
                {t("app.brand")}
              </p>
              <h1
                id="hero-heading"
                className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6 text-white"
              >
                {t("home.hero.title")}
              </h1>
              <p className="text-white/80 text-lg sm:text-xl leading-relaxed max-w-2xl mx-auto mb-8">
                {t("home.hero.subtitle")}
              </p>
              <a
                href="#attractions"
                className="inline-flex items-center justify-center rounded-full bg-brand-primary px-8 py-3 text-sm font-semibold text-white shadow-md hover:bg-brand-primary/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent focus-visible:ring-offset-2 focus-visible:ring-offset-tpgroup-primary min-h-[44px]"
              >
                {t("home.hero.cta")}
              </a>
            </div>
          </section>

          {/* Attraction grid */}
          <section
            id="attractions"
            aria-labelledby="attractions-heading"
            className="py-16 px-4 sm:px-6 lg:px-8 bg-surface"
          >
            <div className="mx-auto max-w-7xl">
              <h2
                id="attractions-heading"
                className="font-display text-3xl font-bold text-text mb-10"
              >
                {t("home.attractions.heading")}
              </h2>

              {loading && (
                <div role="status" aria-live="polite" className="text-center py-16 text-text-muted">
                  <span className="sr-only">Loading attractions</span>
                  <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-brand-primary border-r-transparent" aria-hidden="true" />
                </div>
              )}

              {error && (
                <p role="alert" className="text-center py-16 text-danger">{error}</p>
              )}

              {!loading && !error && list.length === 0 && (
                <p className="text-center py-16 text-text-muted">{t("home.attractions.empty")}</p>
              )}

              {!loading && !error && list.length > 0 && (
                <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 list-none p-0 m-0">
                  {list.map((a) => (
                    <li key={a.id}>
                      <AttractionCard attraction={a} />
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>
        </main>

        <Footer />
      </div>
    </>
  );
}
