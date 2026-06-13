// JSON-LD @graph builder — per SPEC §14 and Schema.org TouristAttraction.
import type { Attraction } from "@/data/types";

const SITE_URL = import.meta.env.VITE_SITE_URL ?? "https://slint-ai-sldc-demo.tpgroupsl.com";

export function buildAttractionSchema(a: Attraction, pageUrl: string) {
  const entity: Record<string, unknown> = {
    "@type": "TouristAttraction",
    "@id": `${pageUrl}#attraction`,
    name: a.name,
    description: a.shortDescription,
    url: pageUrl,
    image: a.images,
    geo: {
      "@type": "GeoCoordinates",
      latitude: a.location.latitude,
      longitude: a.location.longitude,
    },
    address: {
      "@type": "PostalAddress",
      addressLocality: a.location.region,
      addressCountry: "SL",
    },
    aggregateRating: a.reviewCount > 0
      ? {
          "@type": "AggregateRating",
          ratingValue: a.rating,
          reviewCount: a.reviewCount,
          bestRating: 5,
          worstRating: 1,
        }
      : undefined,
    keywords: a.tags.join(", "),
    dateModified: a.lastReviewed,
  };

  if (a.hours.open && a.hours.close) {
    entity["openingHoursSpecification"] = {
      "@type": "OpeningHoursSpecification",
      opens: a.hours.open,
      closes: a.hours.close,
    };
  }

  if (a.faqs && a.faqs.length > 0) {
    entity["mainEntity"] = a.faqs.map((faq) => ({
      "@type": "Question",
      name: faq.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: faq.answer,
      },
    }));
  }

  return entity;
}

export function buildWebSiteSchema() {
  return {
    "@type": "WebSite",
    "@id": `${SITE_URL}#website`,
    name: "Salone Explorer",
    url: SITE_URL,
    description: "Discover Sierra Leone, one attraction at a time.",
    publisher: {
      "@type": "Organization",
      "@id": `${SITE_URL}#organization`,
      name: "FambulTik by TpGroup (SL) Limited",
      url: "https://tpgroupsl.com",
      brand: { "@type": "Brand", name: "FambulTik" },
    },
    potentialAction: {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: `${SITE_URL}/?q={search_term_string}`,
      },
      "query-input": "required name=search_term_string",
    },
  };
}

export function buildGraph(entities: Record<string, unknown>[]) {
  return {
    "@context": "https://schema.org",
    "@graph": entities,
  };
}
