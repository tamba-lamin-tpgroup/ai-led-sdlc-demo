// Per-route SEO head — title, meta description, canonical, og:* tags.
import { Helmet } from "react-helmet-async";
import { t } from "@/lib/content";

interface SeoHeadProps {
  title: string;
  description: string;
  canonical: string;
  image?: string;
  type?: "website" | "article";
}

const DEFAULT_IMAGE = "/og-default.jpg";

export default function SeoHead({
  title,
  description,
  canonical,
  image = DEFAULT_IMAGE,
  type = "website",
}: SeoHeadProps) {
  const siteName = t("app.name");
  const fullTitle = title === siteName ? title : `${title} — ${siteName}`;
  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={canonical} />
      <meta property="og:type" content={type} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={canonical} />
      <meta property="og:image" content={image} />
      <meta property="og:site_name" content={SITE_NAME} />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
    </Helmet>
  );
}
