// Card component for an attraction in the home-page grid.
import { useState } from "react";
import { Link } from "react-router-dom";
import { MapPin, Star } from "lucide-react";
import type { Attraction } from "@/data/types";
import { t } from "@/lib/content";
import { cn, formatRating } from "@/lib/utils";

interface AttractionCardProps {
  attraction: Attraction;
  className?: string;
}

export default function AttractionCard({ attraction, className }: AttractionCardProps) {
  const [imgError, setImgError] = useState(false);
  const href = `/attractions/${attraction.id}`;
  const image = attraction.images[0];
  const showImage = !!image && !imgError;

  return (
    <article className={cn("group rounded-xl border border-border bg-white overflow-hidden shadow-sm hover:shadow-md transition-shadow", className)}>
      <Link
        to={href}
        className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent focus-visible:ring-offset-2 block"
        aria-label={`${t("attraction.card.learnMoreAria")}: ${attraction.name}`}
        tabIndex={0}
      >
        <div className="relative aspect-[16/9] overflow-hidden bg-surface">
          {showImage ? (
            <img
              src={image}
              alt={attraction.name}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
              width={640}
              height={360}
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="flex h-full items-center justify-center bg-brand-sand">
              <MapPin size={32} className="text-brand-primary" aria-hidden="true" />
            </div>
          )}
          <div className="absolute top-2 right-2 flex gap-1 flex-wrap justify-end">
            {attraction.tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-white/90 px-2 py-0.5 text-xs font-medium text-text"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </Link>

      <div className="p-4">
        <Link
          to={href}
          className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded"
        >
          <h2 className="font-display font-semibold text-lg text-text leading-snug group-hover:text-brand-primary transition-colors">
            {attraction.name}
          </h2>
        </Link>

        <div className="mt-1 flex items-center gap-1 text-sm text-text-muted">
          <MapPin size={13} aria-hidden="true" />
          <span>{attraction.location.region}</span>
        </div>

        <p className="mt-2 text-sm text-text-muted line-clamp-2 leading-relaxed">
          {attraction.shortDescription}
        </p>

        <div className="mt-3 flex items-center justify-between">
          {/* role="img" required for aria-label to be announced on a non-interactive element */}
          <div
            role="img"
            aria-label={`${t("attraction.rating")}: ${formatRating(attraction.rating)} ${t("attraction.card.ratingAria")} — ${attraction.reviewCount} ${t("attraction.reviews")}`}
            className="flex items-center gap-1"
          >
            <Star size={14} className="fill-brand-primary text-brand-primary" aria-hidden="true" />
            <span className="text-sm font-medium text-text" aria-hidden="true">{formatRating(attraction.rating)}</span>
            <span className="text-xs text-text-muted" aria-hidden="true">({attraction.reviewCount} {t("attraction.reviews")})</span>
          </div>
          <Link
            to={href}
            className="text-sm font-medium text-brand-accent hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded"
            aria-label={`${t("attraction.card.learnMoreAria")}: ${attraction.name}`}
          >
            {t("attraction.card.learnMore")}
          </Link>
        </div>
      </div>
    </article>
  );
}
