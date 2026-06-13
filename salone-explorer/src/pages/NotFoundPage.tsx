// 404 not-found page — public fallback route.
import { Link } from "react-router-dom";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import SeoHead from "@/components/SeoHead";
import { t } from "@/lib/content";

const SITE_URL = import.meta.env.VITE_SITE_URL ?? "https://slint-ai-sldc-demo.tpgroupsl.com";

export default function NotFoundPage() {
  return (
    <>
      <SeoHead
        title={t("errors.notFound")}
        description={t("errors.notFound.description")}
        canonical={SITE_URL}
      />
      <div className="min-h-screen flex flex-col">
        <NavBar />
        <main
          id="main-content"
          tabIndex={-1}
          className="flex-1 flex flex-col items-center justify-center gap-6 px-4 py-20 text-center"
        >
          <p className="font-display text-8xl font-bold text-brand-sand">404</p>
          <h1 className="font-display text-3xl font-bold text-text">
            {t("errors.notFound")}
          </h1>
          <p className="text-text-muted max-w-md">{t("errors.notFound.description")}</p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-full bg-brand-primary px-8 py-3 text-sm font-semibold text-white hover:bg-brand-primary/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent min-h-[44px]"
          >
            {t("errors.notFound.cta")}
          </Link>
        </main>
        <Footer />
      </div>
    </>
  );
}
