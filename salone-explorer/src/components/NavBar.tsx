// Site navigation bar — FambulTik logo + nav links + skip link.
import { Link, NavLink } from "react-router-dom";
import { t } from "@/lib/content";
import { cn } from "@/lib/utils";

export default function NavBar() {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-border shadow-sm">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-brand-primary focus:px-4 focus:py-2 focus:text-white focus:text-sm focus:font-medium"
      >
        {t("nav.skipToMain")}
      </a>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link
            to="/"
            className="flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent rounded-md"
            aria-label={`${t("app.brand")} — ${t("home.hero.title")}`}
          >
            <span
              className="text-brand-primary font-display font-bold text-xl"
              aria-hidden="true"
            >
              FambulTik
            </span>
            <span className="hidden sm:block text-text-muted text-sm font-medium">
              {t("app.name")}
            </span>
          </Link>

          <nav aria-label={t("nav.ariaMain")}>
            <ul className="flex items-center gap-1 list-none m-0 p-0">
              <li>
                <NavLink
                  to="/"
                  end
                  className={({ isActive }) =>
                    cn(
                      "px-3 py-2 rounded-md text-sm font-medium transition-colors",
                      isActive
                        ? "text-brand-primary bg-brand-sand"
                        : "text-text-muted hover:text-text hover:bg-surface"
                    )
                  }
                >
                  {t("nav.home")}
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/about"
                  className={({ isActive }) =>
                    cn(
                      "px-3 py-2 rounded-md text-sm font-medium transition-colors",
                      isActive
                        ? "text-brand-primary bg-brand-sand"
                        : "text-text-muted hover:text-text hover:bg-surface"
                    )
                  }
                >
                  {t("nav.about")}
                </NavLink>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
}
