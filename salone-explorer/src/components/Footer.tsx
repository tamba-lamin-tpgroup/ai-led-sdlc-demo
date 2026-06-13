// Site footer — disclaimer, copyright, TpGroup endorsement, DS credit.
import { Link } from "react-router-dom";
import { t } from "@/lib/content";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-tpgroup-primary text-white mt-auto" role="contentinfo">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <p className="font-display font-bold text-lg text-brand-sand mb-2">
              {t("app.brand")}
            </p>
            <p className="text-sm text-white/70">{t("footer.tagline")}</p>
          </div>

          <nav aria-label={t("nav.ariaFooter")}>
            <p className="font-semibold text-sm uppercase tracking-wide text-white/50 mb-3">
              {t("footer.links.heading")}
            </p>
            <ul className="space-y-2 list-none m-0 p-0">
              <li>
                <Link
                  to="/"
                  className="text-sm text-white/70 hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded"
                >
                  {t("footer.links.home")}
                </Link>
              </li>
              <li>
                <Link
                  to="/about"
                  className="text-sm text-white/70 hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded"
                >
                  {t("footer.links.about")}
                </Link>
              </li>
            </ul>
          </nav>

          <div>
            <p className="font-semibold text-sm uppercase tracking-wide text-white/50 mb-3">
              Disclaimer
            </p>
            <p className="text-xs text-white/60 leading-relaxed">
              {t("disclaimer.full")}
            </p>
          </div>
        </div>

        <div className="border-t border-white/10 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-white/50">
            &copy; {year} {t("footer.copyright")} {t("footer.publisher")}
          </p>
          <p className="text-xs text-white/40">{t("footer.credit")}</p>
        </div>
      </div>
    </footer>
  );
}
