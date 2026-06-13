// About page — FambulTik brand, disclaimer, data sources. Public route at /about.
import { ExternalLink } from "lucide-react";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import SeoHead from "@/components/SeoHead";
import JsonLd from "@/components/JsonLd";
import { t, getSources } from "@/lib/content";
import { buildGraph, buildWebSiteSchema } from "@/seo/graph";

const SITE_URL = import.meta.env.VITE_SITE_URL ?? "https://slint-ai-sldc-demo.tpgroupsl.com";
const SOURCES = getSources();

export default function AboutPage() {
  const graph = buildGraph([buildWebSiteSchema()]);

  return (
    <>
      <SeoHead
        title={t("about.heading")}
        description={t("app.tagline")}
        canonical={`${SITE_URL}/about`}
      />
      <JsonLd graph={graph} />

      <div className="min-h-screen flex flex-col">
        <NavBar />

        <main id="main-content" tabIndex={-1}>
          <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-16">
            <h1 className="font-display text-4xl font-bold text-text mb-8">
              {t("about.heading")}
            </h1>

            {/* Brand */}
            <section aria-labelledby="brand-heading" className="mb-12">
              <h2 id="brand-heading" className="font-display text-2xl font-semibold text-text mb-4">
                {t("app.brand")}
              </h2>
              <p className="text-text leading-relaxed">{t("about.brand")}</p>
            </section>

            {/* Disclaimer */}
            <section
              aria-labelledby="disclaimer-heading"
              className="mb-12 rounded-xl border border-warning/30 bg-brand-sand p-6"
            >
              <h2 id="disclaimer-heading" className="font-display text-2xl font-semibold text-text mb-4">
                {t("about.disclaimer.heading")}
              </h2>
              <p className="text-text leading-relaxed">{t("disclaimer.full")}</p>
            </section>

            {/* Data sources */}
            <section aria-labelledby="sources-heading" className="mb-12">
              <h2 id="sources-heading" className="font-display text-2xl font-semibold text-text mb-4">
                {t("about.sources.heading")}
              </h2>
              <p className="text-text-muted mb-4">{t("about.sources.intro")}</p>
              <ul className="space-y-2 list-none m-0 p-0">
                {SOURCES.map((s) => (
                  <li key={s.url}>
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-brand-accent hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded"
                    >
                      {s.name}
                      <ExternalLink size={13} aria-label="(opens in new tab)" />
                    </a>
                  </li>
                ))}
              </ul>
            </section>

            {/* DS credit */}
            <section aria-labelledby="ds-heading">
              <h2 id="ds-heading" className="sr-only">Design credits</h2>
              <p className="text-sm text-text-muted">
                {t("about.ds.credit")}{" "}
                <a
                  href="https://design.tpgroupsl.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-brand-accent hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded"
                >
                  TpGroup Design System
                  <ExternalLink size={12} className="inline ml-0.5" aria-label="(opens in new tab)" />
                </a>
              </p>
            </section>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
