// Attraction detail page — /attractions/:id. Public route.
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  MapPin, Clock, Star, ExternalLink, ChevronRight,
} from "lucide-react";
import * as Accordion from "@radix-ui/react-accordion";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import SeoHead from "@/components/SeoHead";
import JsonLd from "@/components/JsonLd";
import { attractions, t } from "@/lib/content";
import { buildAttractionSchema, buildGraph, buildWebSiteSchema } from "@/seo/graph";
import { buildMapsUrl, cn, formatRating } from "@/lib/utils";
import type { Attraction } from "@/data/types";

const SITE_URL = import.meta.env.VITE_SITE_URL ?? "https://slint-ai-sldc-demo.tpgroupsl.com";

export default function AttractionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [attraction, setAttraction] = useState<Attraction | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!id) { setNotFound(true); setLoading(false); return; }
    attractions
      .getById(id)
      .then((a) => {
        if (!a) setNotFound(true);
        else setAttraction(a);
      })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <NavBar />
        <main id="main-content" tabIndex={-1} className="flex-1 flex items-center justify-center">
          <div role="status" aria-live="polite">
            <span className="sr-only">Loading attraction</span>
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-primary border-r-transparent" aria-hidden="true" />
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (notFound || !attraction) {
    const pageUrl = `${SITE_URL}/attractions/${id ?? ""}`;
    return (
      <>
        <SeoHead
          title={t("attraction.notFound")}
          description={t("attraction.notFound.description")}
          canonical={pageUrl}
        />
        <div className="min-h-screen flex flex-col">
          <NavBar />
          <main id="main-content" tabIndex={-1} className="flex-1 flex flex-col items-center justify-center gap-4 px-4 py-16">
            <h1 className="font-display text-3xl font-bold text-text">{t("attraction.notFound")}</h1>
            <p className="text-text-muted">{t("attraction.notFound.description")}</p>
            <Link
              to="/"
              className="inline-flex items-center gap-2 rounded-full bg-brand-primary px-6 py-2.5 text-sm font-semibold text-white hover:bg-brand-primary/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent min-h-[44px]"
            >
              {t("attraction.backToHome")}
            </Link>
          </main>
          <Footer />
        </div>
      </>
    );
  }

  const pageUrl = `${SITE_URL}/attractions/${attraction.id}`;
  const graph = buildGraph([buildWebSiteSchema(), buildAttractionSchema(attraction, pageUrl)]);
  const mapsUrl = buildMapsUrl(
    attraction.location.latitude,
    attraction.location.longitude,
    attraction.name
  );

  return (
    <>
      <SeoHead
        title={attraction.name}
        description={attraction.shortDescription}
        canonical={pageUrl}
        image={attraction.images[0]}
        type="article"
      />
      <JsonLd graph={graph} />

      <div className="min-h-screen flex flex-col">
        <NavBar />

        <main id="main-content" tabIndex={-1}>
          {/* Breadcrumb */}
          <nav
            aria-label="Breadcrumb"
            className="bg-surface border-b border-border px-4 sm:px-6 lg:px-8 py-3"
          >
            <ol className="mx-auto max-w-7xl flex items-center gap-1 text-sm text-text-muted list-none m-0 p-0">
              <li>
                <Link to="/" className="hover:text-text transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded">
                  {t("attraction.breadcrumb.home")}
                </Link>
              </li>
              <li aria-hidden="true"><ChevronRight size={14} /></li>
              <li>
                <Link to="/#attractions" className="hover:text-text transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded">
                  {t("attraction.breadcrumb.attractions")}
                </Link>
              </li>
              <li aria-hidden="true"><ChevronRight size={14} /></li>
              <li aria-current="page" className="text-text font-medium truncate max-w-[200px]">
                {attraction.name}
              </li>
            </ol>
          </nav>

          {/* Hero image */}
          {attraction.images.length > 0 && (
            <div className="relative h-64 sm:h-96 overflow-hidden bg-surface">
              <img
                src={attraction.images[0]}
                alt={attraction.name}
                className="h-full w-full object-cover"
                width={1280}
                height={720}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" aria-hidden="true" />
            </div>
          )}

          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-10">
            {/* Title block */}
            <div className="mb-8">
              <div className="flex flex-wrap gap-2 mb-3">
                {attraction.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-brand-sand px-3 py-1 text-xs font-medium text-text"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <h1 className="font-display text-4xl font-bold text-text leading-tight mb-2">
                {attraction.name}
              </h1>
              <div className="flex items-center gap-2 text-text-muted">
                <MapPin size={16} aria-hidden="true" />
                <span>{attraction.location.region}</span>
              </div>
              <div className="mt-3 flex items-center gap-2">
                <div
                  className="flex items-center gap-1"
                  aria-label={`${t("attraction.rating")}: ${formatRating(attraction.rating)} out of 5 from ${attraction.reviewCount} ${t("attraction.reviews")}`}
                >
                  <Star size={16} className="fill-brand-primary text-brand-primary" aria-hidden="true" />
                  <span className="font-semibold text-text">{formatRating(attraction.rating)}</span>
                  <span className="text-sm text-text-muted">
                    ({attraction.reviewCount} {t("attraction.reviews")})
                  </span>
                </div>
              </div>
            </div>

            {/* Description */}
            <section aria-labelledby="description-heading" className="mb-10">
              <h2 id="description-heading" className="sr-only">About this attraction</h2>
              <div className="prose max-w-none">
                {attraction.longDescription.split("\n\n").map((para, i) => (
                  <p key={i} className="text-text leading-relaxed mb-4">
                    {para}
                  </p>
                ))}
              </div>
            </section>

            {/* Hours + Directions */}
            <section
              aria-labelledby="hours-heading"
              className="mb-10 rounded-xl border border-border bg-surface p-6"
            >
              <h2 id="hours-heading" className="font-display font-semibold text-lg text-text mb-4 flex items-center gap-2">
                <Clock size={18} aria-hidden="true" />
                {t("attraction.openingHours")}
              </h2>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <dt className="font-medium text-text-muted">{t("attraction.daysOpen")}</dt>
                  <dd className="text-text mt-0.5">{attraction.hours.daysOpen}</dd>
                </div>
                <div>
                  <dt className="font-medium text-text-muted">Hours</dt>
                  <dd className="text-text mt-0.5">{attraction.hours.open} – {attraction.hours.close}</dd>
                </div>
                {attraction.hours.notes && (
                  <div className="sm:col-span-2">
                    <dt className="font-medium text-text-muted">{t("attraction.hoursNotes")}</dt>
                    <dd className="text-text mt-0.5">{attraction.hours.notes}</dd>
                  </div>
                )}
              </dl>

              <div className="mt-6">
                <a
                  href={mapsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-full bg-brand-primary px-6 py-2.5 text-sm font-semibold text-white hover:bg-brand-primary/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent min-h-[44px]"
                  aria-label={t("attraction.directions.label")}
                >
                  <MapPin size={16} aria-hidden="true" />
                  {t("attraction.directions.cta")}
                  <ExternalLink size={14} aria-hidden="true" />
                </a>
              </div>
            </section>

            {/* Video embed */}
            {attraction.videoUrl && (
              <section aria-labelledby="video-heading" className="mb-10">
                <h2 id="video-heading" className="font-display font-semibold text-lg text-text mb-4">
                  {t("attraction.videoLabel")}
                </h2>
                <div className="relative aspect-video rounded-xl overflow-hidden">
                  <iframe
                    src={attraction.videoUrl.replace("watch?v=", "embed/") + "?cc_load_policy=1"}
                    title={`${attraction.name} video tour`}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="absolute inset-0 h-full w-full"
                    loading="lazy"
                  />
                </div>
              </section>
            )}

            {/* FAQ */}
            {attraction.faqs && attraction.faqs.length > 0 && (
              <section aria-labelledby="faq-heading" className="mb-10">
                <h2 id="faq-heading" className="font-display font-semibold text-xl text-text mb-6">
                  {t("attraction.faqs.heading")}
                </h2>
                <Accordion.Root type="single" collapsible className="space-y-2">
                  {attraction.faqs.map((faq, i) => (
                    <Accordion.Item
                      key={i}
                      value={`faq-${i}`}
                      className="rounded-lg border border-border bg-white overflow-hidden"
                    >
                      <Accordion.Header>
                        <Accordion.Trigger
                          className={cn(
                            "flex w-full items-center justify-between px-5 py-4 text-left text-sm font-medium text-text",
                            "hover:bg-surface transition-colors",
                            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand-accent",
                            "[&[data-state=open]>svg]:rotate-180"
                          )}
                        >
                          {faq.question}
                          <ChevronRight
                            size={16}
                            className="flex-shrink-0 rotate-90 transition-transform text-text-muted"
                            aria-hidden="true"
                          />
                        </Accordion.Trigger>
                      </Accordion.Header>
                      <Accordion.Content className="px-5 pb-4 text-sm text-text-muted leading-relaxed data-[state=open]:animate-none">
                        {faq.answer}
                      </Accordion.Content>
                    </Accordion.Item>
                  ))}
                </Accordion.Root>
              </section>
            )}

            {/* Sources */}
            {attraction.sources.length > 0 && (
              <section aria-labelledby="sources-heading" className="mb-10">
                <h2 id="sources-heading" className="font-display font-semibold text-lg text-text mb-4">
                  {t("attraction.sources.heading")}
                </h2>
                <ul className="space-y-1 text-sm list-none m-0 p-0">
                  {attraction.sources.map((src) => (
                    <li key={src}>
                      <a
                        href={src}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-brand-accent hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded inline-flex items-center gap-1"
                      >
                        {src}
                        <ExternalLink size={12} aria-label="(opens in new tab)" />
                      </a>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
