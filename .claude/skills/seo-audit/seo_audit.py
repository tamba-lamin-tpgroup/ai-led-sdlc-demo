"""
Generic SEO & GEO Audit Script.

Runs a full SEO audit on any website — local or remote. Accepts an existing
crawl inventory (from crawler.py) or runs its own URL discovery from sitemap.

Usage:
    python3 seo_audit.py --url https://example.com
    python3 seo_audit.py --url https://example.com --geo --pptx
    python3 seo_audit.py --input ./crawl-output --client "Acme" --geo
    python3 seo_audit.py --url https://mysite.ddev.site --local --max-pages 5000
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

try:
    import extruct
    HAS_EXTRUCT = True
except ImportError:
    HAS_EXTRUCT = False

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generic SEO & GEO Audit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--url", default=None, help="Base URL to audit")
    p.add_argument("--input", default=None, dest="input_dir",
                   help="Use existing crawl output directory from /crawl-site")
    p.add_argument("--local", action="store_true",
                   help="Local/dev site: disable SSL verification")
    p.add_argument("--sitemap", default=None,
                   help="Sitemap URL or local XML file path")
    p.add_argument("--max-pages", type=int, default=1000)
    p.add_argument("--output", default="./seo-audit-output")
    p.add_argument("--exclude", action="append", default=[])
    p.add_argument("--scope", default=None)
    p.add_argument("--geo", action="store_true", help="Include GEO / AI crawlability analysis")
    p.add_argument("--client", default="Website")
    p.add_argument("--company", default="SEO Audit")
    p.add_argument("--brand-color", default="#1a1a2e")
    p.add_argument("--cms", choices=["drupal", "wordpress", "generic"], default="generic")
    p.add_argument("--pptx", action="store_true", help="Generate PowerPoint report")
    p.add_argument("--concurrency", type=int, default=5)
    p.add_argument("--timeout", type=int, default=15)
    return p


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

def make_session(args) -> requests.Session:
    sess = requests.Session()
    sess.headers.update({"User-Agent": "SEO-Audit-Bot/1.0 (not-indexing)"})
    if args.local:
        import urllib3
        urllib3.disable_warnings()
        sess.verify = False
    return sess


# ---------------------------------------------------------------------------
# URL loading (from crawl-site output or fresh sitemap)
# ---------------------------------------------------------------------------

def load_urls_from_input(input_dir: str) -> list[str]:
    crawl_list = os.path.join(input_dir, "urls-to-crawl.txt")
    inventory = os.path.join(input_dir, "inventory.csv")
    if os.path.exists(crawl_list):
        with open(crawl_list, encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip()]
    if os.path.exists(inventory):
        with open(inventory, encoding="utf-8") as fh:
            return [row["url"] for row in csv.DictReader(fh) if row.get("url")]
    raise FileNotFoundError(f"No URL list found in {input_dir}")


def discover_urls_from_sitemap(url: str, session, args) -> list[str]:
    """Lightweight sitemap fetch — calls crawler.py's logic inline."""
    from xml.etree import ElementTree as ET

    SM_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    base_host = urlparse(url).netloc
    sitemap_source = args.sitemap or (url.rstrip("/") + "/sitemap.xml")
    seen: set[str] = set()
    urls: list[str] = []

    def _fetch(src):
        if os.path.isfile(src):
            return open(src, "rb").read()
        try:
            r = session.get(src, timeout=20)
            return r.content if r.status_code == 200 else None
        except Exception:
            return None

    def _process(src):
        if src in seen:
            return
        seen.add(src)
        raw = _fetch(src)
        if not raw:
            return
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            return
        children = [el.text.strip() for el in root.findall(".//sm:sitemap/sm:loc", SM_NS) if el.text]
        if not children:
            children = [el.text.strip() for el in root.findall(".//sitemap/loc") if el.text]
        for child in children:
            if "page=" in child:
                base = re.sub(r"[?&]page=\d+", "", child)
                sep = "?" if "?" not in base else "&"
                for pg in range(1, 200):
                    paged = f"{base}{sep}page={pg}"
                    r = _fetch(paged)
                    if not r:
                        break
                    try:
                        proot = ET.fromstring(r)
                    except ET.ParseError:
                        break
                    entries = [el.text.strip() for el in proot.findall(".//sm:url/sm:loc", SM_NS) if el.text]
                    if not entries:
                        break
                    urls.extend(entries)
                    time.sleep(0.05)
            else:
                _process(child)
        for el in (root.findall(".//sm:url/sm:loc", SM_NS) or root.findall(".//url/loc")):
            if el.text:
                urls.append(el.text.strip())

    _process(sitemap_source)

    # Rewrite host if sitemap entries use a different host
    clean: list[str] = []
    for u in urls:
        parsed = urlparse(u)
        if parsed.netloc and parsed.netloc != base_host:
            u = parsed._replace(netloc=base_host).geturl()
        if not any(re.search(pat, u) for pat in args.exclude):
            clean.append(u)

    # Deduplicate
    seen_urls: set[str] = set()
    result: list[str] = []
    for u in clean:
        if u not in seen_urls:
            seen_urls.add(u)
            result.append(u)

    cap = args.max_pages or len(result)
    return result[:cap]


# ---------------------------------------------------------------------------
# Single-URL SEO crawl
# ---------------------------------------------------------------------------

def _text(tag) -> str:
    return tag.get_text(separator=" ", strip=True) if tag else ""


def _schema_types(soup: BeautifulSoup) -> list[str]:
    types: list[str] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            t = item.get("@type", "")
            (types.extend(t) if isinstance(t, list) else types.append(t)) if t else None
    return list(set(types))


def crawl_url(url: str, session, timeout: int) -> dict:
    base_host = urlparse(url).netloc
    row = dict(
        url=url, http_status=None, redirect_target="", redirect_chain_length=0,
        title_tag="", title_length=0, title_missing=True,
        title_duplicate_flag=False, meta_description="",
        meta_description_length=0, meta_description_missing=True,
        meta_description_duplicate_flag=False,
        canonical_url="", canonical_is_self=False,
        canonical_missing=True, canonical_conflict=False,
        meta_robots="", x_robots_tag="",
        h1_text="", h1_count=0, h1_missing=True,
        h2_count=0, h3_count=0, word_count=0,
        image_count=0, images_missing_alt=0, images_with_empty_alt=0,
        internal_link_count=0, external_link_count=0,
        has_og_title=False, has_og_description=False, has_og_image=False,
        has_twitter_card=False, schema_types_present="", schema_count=0,
        response_time_ms=0, has_noindex=False, has_nofollow_page=False,
        content_type="", last_modified_header="", page_size_bytes=0,
    )
    try:
        t0 = time.monotonic()
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        row["response_time_ms"] = int((time.monotonic() - t0) * 1000)
        row["http_status"] = resp.status_code
        row["content_type"] = resp.headers.get("Content-Type", "")
        row["x_robots_tag"] = resp.headers.get("X-Robots-Tag", "")
        row["last_modified_header"] = resp.headers.get("Last-Modified", "")
        row["page_size_bytes"] = len(resp.content)
        if resp.history:
            row["redirect_chain_length"] = len(resp.history)
            row["redirect_target"] = resp.url
        if resp.status_code != 200 or "text/html" not in row["content_type"]:
            return row
        soup = BeautifulSoup(resp.text, "lxml")
        t = _text(soup.find("title"))
        row.update(title_tag=t, title_length=len(t), title_missing=not t)
        md_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        md = (md_tag.get("content", "") or "").strip() if md_tag else ""
        row.update(meta_description=md, meta_description_length=len(md), meta_description_missing=not md)
        canon = soup.find("link", rel=lambda r: r and "canonical" in r)
        if canon:
            ch = canon.get("href", "").strip()
            pu, pc = urlparse(url), urlparse(ch)
            row.update(
                canonical_url=ch, canonical_missing=False,
                canonical_is_self=(pc.path.rstrip("/") == pu.path.rstrip("/")),
                canonical_conflict=bool(re.match(r"^/node/\d+$", pc.path)),
            )
        rb = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
        rc = (rb.get("content", "") or "").lower() if rb else ""
        row.update(meta_robots=rc, has_noindex="noindex" in rc, has_nofollow_page="nofollow" in rc)
        h1s = soup.find_all("h1")
        row.update(h1_count=len(h1s), h1_missing=not h1s,
                   h1_text=_text(h1s[0]) if h1s else "",
                   h2_count=len(soup.find_all("h2")),
                   h3_count=len(soup.find_all("h3")))
        body = soup.find("body")
        if body:
            for s in body(["script", "style"]):
                s.decompose()
            row["word_count"] = len(body.get_text(separator=" ").split())
        imgs = soup.find_all("img")
        row.update(image_count=len(imgs),
                   images_missing_alt=sum(1 for i in imgs if not i.get("alt")),
                   images_with_empty_alt=sum(1 for i in imgs if i.get("alt") == ""))
        internal = external = 0
        for a in soup.find_all("a", href=True):
            h = a["href"].strip()
            if not h or h.startswith(("#", "mailto:", "tel:")):
                continue
            abs_h = urljoin(url, h)
            ph = urlparse(abs_h)
            if ph.netloc == base_host or not ph.netloc:
                internal += 1
            else:
                external += 1
        row.update(internal_link_count=internal, external_link_count=external)
        row.update(
            has_og_title=bool(soup.find("meta", property="og:title")),
            has_og_description=bool(soup.find("meta", property="og:description")),
            has_og_image=bool(soup.find("meta", property="og:image")),
            has_twitter_card=bool(soup.find("meta", attrs={"name": re.compile(r"twitter:card", re.I)})),
        )
        st = _schema_types(soup)
        row.update(schema_types_present=", ".join(st), schema_count=len(st))
    except requests.Timeout:
        row["http_status"] = "TIMEOUT"
    except Exception:
        row["http_status"] = "ERROR"
    return row


# ---------------------------------------------------------------------------
# GEO audit
# ---------------------------------------------------------------------------

def geo_audit_url(url: str, session, timeout: int) -> dict:
    row = dict(url=url, http_status=None, schema_types_found="",
               has_organization_schema=False, has_person_schema=False,
               has_article_schema=False, has_event_schema=False,
               has_faq_schema=False, has_howto_schema=False,
               has_breadcrumb_schema=False, has_webpage_schema=False,
               has_video_schema=False, has_jobposting_schema=False,
               has_speakable_schema=False,
               entity_id_present=False, sameAs_present=False,
               organization_name_consistent=False,
               has_og_complete=False, has_twitter_card_complete=False,
               schema_validation_errors="",
               modification_date="", faq_pattern_no_schema=False,
               js_rendering_risk=False, has_byline=False, has_date_published=False)
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        row["http_status"] = resp.status_code
        if resp.status_code != 200:
            return row
        soup = BeautifulSoup(resp.text, "lxml")
        # JSON-LD blocks
        blocks: list[dict] = []
        for tag in soup.find_all("script", type="application/ld+json"):
            try:
                d = json.loads(tag.string or "")
                (blocks.extend(d) if isinstance(d, list) else blocks.append(d)) if d else None
            except Exception:
                pass

        def _all_types(obj, depth=0):
            if depth > 4:
                return []
            ts = []
            if isinstance(obj, list):
                for i in obj:
                    ts.extend(_all_types(i, depth + 1))
            elif isinstance(obj, dict):
                t = obj.get("@type", "")
                (ts.extend(t) if isinstance(t, list) else ts.append(t)) if t else None
                for v in obj.values():
                    if isinstance(v, (dict, list)):
                        ts.extend(_all_types(v, depth + 1))
            return ts

        all_types = _all_types(blocks)
        row["schema_types_found"] = ", ".join(sorted(set(all_types)))
        type_checks = {
            "has_organization_schema": "Organization",
            "has_person_schema": "Person",
            "has_article_schema": "Article",
            "has_event_schema": "Event",
            "has_faq_schema": "FAQPage",
            "has_howto_schema": "HowTo",
            "has_breadcrumb_schema": "BreadcrumbList",
            "has_webpage_schema": "WebPage",
            "has_video_schema": "VideoObject",
            "has_jobposting_schema": "JobPosting",
            "has_speakable_schema": "SpeakableSpecification",
        }
        for field, type_name in type_checks.items():
            row[field] = type_name in all_types
        for block in blocks:
            if block.get("@id"):
                row["entity_id_present"] = True
            if block.get("sameAs"):
                row["sameAs_present"] = True
            if "Organization" in (_all_types(block)):
                name = block.get("name", "")
                row["organization_name_consistent"] = bool(name)
        row["has_og_complete"] = bool(
            soup.find("meta", property="og:title") and
            soup.find("meta", property="og:description") and
            soup.find("meta", property="og:image")
        )
        row["has_twitter_card_complete"] = bool(
            soup.find("meta", attrs={"name": re.compile(r"twitter:card", re.I)}) and
            soup.find("meta", attrs={"name": re.compile(r"twitter:title", re.I)})
        )
        # FAQ pattern detection
        faq_selectors = ["dl dt", "details summary", ".faq h3", ".faq h4",
                         ".accordion-title", ".faq-question"]
        has_faq_pattern = any(soup.select(s) for s in faq_selectors)
        if not has_faq_pattern:
            has_faq_pattern = any(
                tag.get_text(strip=True).endswith("?")
                for tag in soup.find_all(["h3", "h4", "h2"])
            )
        row["faq_pattern_no_schema"] = has_faq_pattern and not row["has_faq_schema"]
        # E-E-A-T
        byline_selectors = [".author", ".byline", "[rel=author]", ".field--name-field-author",
                            ".entry-author", ".post-author"]
        row["has_byline"] = any(soup.select(s) for s in byline_selectors)
        date_selectors = ["time[datetime]", "meta[property='article:published_time']",
                          ".field--name-field-date", ".entry-date", ".published"]
        row["has_date_published"] = any(soup.select(s) for s in date_selectors)
        # Modification date
        for block in blocks:
            for f in ["dateModified", "datePublished"]:
                if block.get(f):
                    row["modification_date"] = str(block[f])
                    break
        if not row["modification_date"]:
            tt = soup.find("meta", property="article:modified_time")
            if tt:
                row["modification_date"] = tt.get("content", "")
        # JS rendering risk
        body = soup.find("body")
        raw_text = len(body.get_text(separator=" ", strip=True)) if body else 0
        has_fw = bool(soup.find("div", id=re.compile(r"^(app|root)$")) or
                      re.search(r"(react|vue|angular|next\.js)", resp.text, re.I))
        row["js_rendering_risk"] = has_fw and raw_text < 500
        # Schema validation errors
        errors = []
        for block in blocks:
            types = _all_types(block)
            if "Article" in types or "NewsArticle" in types:
                for req in ["headline", "author", "datePublished", "publisher"]:
                    if not block.get(req):
                        errors.append(f"Article missing {req}")
            if "Event" in types:
                for req in ["name", "startDate", "location"]:
                    if not block.get(req):
                        errors.append(f"Event missing {req}")
            if "FAQPage" in types and not block.get("mainEntity"):
                errors.append("FAQPage missing mainEntity")
            if "BreadcrumbList" in types and not block.get("itemListElement"):
                errors.append("BreadcrumbList missing itemListElement")
        row["schema_validation_errors"] = "; ".join(errors)
    except Exception:
        row["http_status"] = "ERROR"
    return row


# ---------------------------------------------------------------------------
# robots.txt and llms.txt
# ---------------------------------------------------------------------------

def check_robots(base_url: str, session, timeout: int) -> dict:
    url = base_url.rstrip("/") + "/robots.txt"
    try:
        resp = session.get(url, timeout=timeout)
        content = resp.text if resp.status_code == 200 else ""
    except Exception:
        return {"error": "fetch_failed"}

    AI_BOTS = ["GPTBot", "ClaudeBot", "PerplexityBot", "GoogleOther",
               "CCBot", "anthropic-ai", "ChatGPT-User"]
    disallow_lines: list[str] = []
    current_agents: list[str] = []
    blocked_ai: list[str] = []

    for line in content.splitlines():
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            current_agents = [line[len("user-agent:"):].strip()]
        elif line.lower().startswith("disallow:"):
            path = line[len("disallow:"):].strip()
            disallow_lines.append(path)
            if path in ("/", "/*"):
                for bot in AI_BOTS:
                    if any(bot.lower() in a.lower() for a in current_agents):
                        if bot not in blocked_ai:
                            blocked_ai.append(bot)

    return {
        "total_disallow_rules": len(disallow_lines),
        "blocked_ai_bots": ", ".join(blocked_ai) or "None detected",
        "has_broad_block": any(d in ("/", "/*") for d in disallow_lines),
        "has_admin_rule": any("/admin" in d for d in disallow_lines),
        "has_jsonapi_rule": any("/jsonapi" in d for d in disallow_lines),
        "has_pagination_rule": any(
            any(p in d for p in ["?page=", "?sort=", "?filter="])
            for d in disallow_lines
        ),
        "raw_snippet": content[:2000],
    }


def check_llms_txt(base_url: str, session, timeout: int) -> dict:
    url = base_url.rstrip("/") + "/llms.txt"
    try:
        resp = session.get(url, timeout=timeout)
        if resp.status_code == 200:
            return {"present": True, "status": resp.status_code,
                    "length_chars": len(resp.text), "preview": resp.text[:300]}
    except Exception:
        pass
    return {"present": False, "status": 404, "length_chars": 0, "preview": ""}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def compute_seo_score(total_200: int, missing_title: int, dup_titles: int,
                      missing_desc: int, dup_desc: int, missing_h1: int,
                      errors_4xx: int, errors_5xx: int,
                      missing_canon: int, canon_conflict: int,
                      img_alt_pages: int, crawl_budget_critical: bool) -> dict:
    t = total_200 or 1

    def _s(bad, weight):
        return weight * max(0.0, 1.0 - (bad / t) * 3)

    scores = {
        "title":     _s(missing_title + dup_titles // 2, 20),
        "meta_desc": _s(missing_desc + dup_desc // 2, 20),
        "h1":        _s(missing_h1, 10),
        "errors":    _s(errors_4xx + errors_5xx * 2, 20),
        "canonical": _s(missing_canon + canon_conflict, 10),
        "images":    _s(img_alt_pages, 10),
        "crawl":     0 if crawl_budget_critical else 10,
    }
    scores["total"] = min(100, int(sum(scores.values())))
    return {k: int(v) for k, v in scores.items()}


def write_executive_summary(d: dict, out_dir: str, audit_date: str) -> None:
    t = d["total_200"] or 1
    seo = d["seo_score"]
    path = os.path.join(out_dir, "reports", "00_executive_summary.md")

    lines = [
        f"# {d['client']} — SEO & GEO Audit: Executive Summary\n",
        f"**Prepared by:** {d['company']}  ",
        f"**Audit Date:** {audit_date}  ",
        f"**Scope:** {d['total']:,} URLs crawled from {d['base_url']}\n",
        "---\n",
        "## SEO Health Score\n",
        f"**Overall: {seo['total']}/100**\n",
        "| Dimension | Score | Finding |",
        "|---|---|---|",
        f"| Title Tags | {seo['title']}/20 | {d['missing_title']:,} missing, {d['dup_titles']:,} duplicates |",
        f"| Meta Descriptions | {seo['meta_desc']}/20 | {d['missing_desc']:,} missing ({100*d['missing_desc']//t}%) |",
        f"| Heading Structure | {seo['h1']}/10 | {d['missing_h1']:,} pages missing H1 |",
        f"| HTTP Errors | {seo['errors']}/20 | {d['errors_4xx']:,} 4xx, {d['errors_5xx']:,} 5xx |",
        f"| Canonical Tags | {seo['canonical']}/10 | {d['missing_canon']:,} missing, {d['canon_conflict']:,} conflicts |",
        f"| Image Alt Text | {seo['images']}/10 | {d['img_alt_pages']:,} pages with missing alt |",
        f"| Crawl Budget | {seo['crawl']}/10 | {'Critical issues found' if d['crawl_budget_critical'] else 'No critical issues'} |",
        "",
    ]

    if d.get("geo"):
        geo = d.get("geo_score", {})
        lines += [
            "## GEO Readiness Score\n",
            "| Dimension | Score | Evidence |",
            "|---|---|---|",
            f"| Structured Data Coverage | {geo.get('structured_data', 0)}/10 | {d.get('geo_schema_pct', '0%')} of pages have schema |",
            f"| Entity Relationship Clarity | {geo.get('entity_clarity', 0)}/10 | Organization schema: {d.get('has_org_schema', 0):,} pages |",
            f"| AI Crawlability | {geo.get('ai_crawlability', 0)}/10 | llms.txt: {'Present' if d.get('llms_present') else 'Absent'} |",
            f"| E-E-A-T Signal Strength | {geo.get('eeat', 0)}/10 | Author attribution: {d.get('byline_pct', '0%')} |",
            f"| Content Depth & Citability | {geo.get('citability', 0)}/10 | {d.get('faq_opportunities', 0):,} FAQ schema opportunities |",
            f"| Search & Findability | {geo.get('findability', 0)}/10 | BreadcrumbList: {d.get('breadcrumb_pct', '0%')} coverage |",
            f"| **OVERALL** | **{geo.get('overall', 0)}/10** | |",
            "",
        ]

    lines += [
        "## Top Issues\n",
        "| Priority | Issue | Severity | Affected |",
        "|---|---|---|---|",
    ]
    for i, rec in enumerate(d.get("recommendations", [])[:10], 1):
        lines.append(
            f"| {i} | {rec['issue_title'][:70]} | {rec['severity']} | {rec['affected_url_count']:,} |"
        )

    lines += [
        "",
        "## Recommended Immediate Actions (< 1 week)\n",
        "1. Fix robots.txt: block admin paths, API endpoints, and any URL patterns generating noise",
        "2. Configure meta description token templates for all content types",
        "3. Create llms.txt — a 1-2 page AI-readable site summary (if --geo identified this gap)",
        "4. Remove 4xx/5xx URLs from the XML sitemap",
        "",
        "## Recommended Strategic Actions (1–3 months)\n",
        "1. Implement BreadcrumbList schema sitewide",
        "2. Add Article/NewsArticle schema to all editorial content types",
        "3. Add FAQPage schema to Q&A and help content",
        "4. Resolve duplicate title tags via per-content-type Metatag token configuration",
        "5. Audit and fix image alt text coverage",
    ]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def write_seo_findings(d: dict, out_dir: str, audit_date: str) -> None:
    t = d["total_200"] or 1
    path = os.path.join(out_dir, "reports", "01_seo_findings.md")

    def pct(n): return f"{100*n//t}%" if t else "0%"
    def samples(lst, n=5): return "\n".join(f"  - {u}" for u in lst[:n]) or "  - (none)"

    cms_notes = {
        "drupal": "Drupal: configure Metatag module token patterns per content type.",
        "wordpress": "WordPress: configure Yoast SEO / RankMath template tokens.",
        "generic": "Configure your CMS meta tag module with per-page token values.",
    }
    cms_hint = cms_notes.get(d.get("cms", "generic"), cms_notes["generic"])

    lines = [
        f"# {d['client']} — SEO Findings\n",
        f"**Audit Date:** {audit_date} | **Pages audited:** {d['total']:,} | **HTTP 200:** {d['total_200']:,}\n",
        "---\n",
        "## 1. On-Page SEO\n",
        "### 1.1 Title Tags\n",
        f"**Missing titles:** {d['missing_title']:,} ({pct(d['missing_title'])}) — Severity: **Critical**",
        f"\n{samples(d.get('missing_title_samples', []))}",
        f"\n_Fix:_ {cms_hint} Target 50–60 character titles.\n",
        f"**Duplicate titles:** {d['dup_titles']:,} ({pct(d['dup_titles'])}) — Severity: **Critical**",
        "\n_Fix:_ Ensure token produces unique per-page output. Avoid static global fallbacks.\n",
        f"**Short titles (< 30 chars):** {d.get('short_titles', 0):,} — Severity: **Medium**\n",
        f"**Long titles (> 60 chars):** {d.get('long_titles', 0):,} — Severity: **Low**\n",
        "### 1.2 Meta Descriptions\n",
        f"**Missing descriptions:** {d['missing_desc']:,} ({pct(d['missing_desc'])}) — Severity: **Critical**",
        f"\n{samples(d.get('missing_desc_samples', []))}",
        f"\n_Fix:_ {cms_hint} Target 120–160 characters. Use body summary or teaser field as source.\n",
        f"**Duplicate descriptions:** {d['dup_descs']:,} — Severity: **High**\n",
        "### 1.3 H1 Headings\n",
        f"**Missing H1:** {d['missing_h1']:,} ({pct(d['missing_h1'])}) — Severity: **High**",
        "\n_Fix:_ Audit page templates — ensure content title is wrapped in `<h1>`.\n",
        "---\n",
        "## 2. Technical SEO\n",
        "### 2.1 HTTP Errors\n",
        f"**4xx errors:** {d['errors_4xx']:,} — Severity: **High**",
        f"\n{samples(d.get('error_404_samples', []))}",
        "\n_Fix:_ Implement 301 redirects or remove from sitemap. Clean up deleted content.\n",
        f"**5xx errors:** {d['errors_5xx']:,} — Severity: **Critical**",
        f"\n{samples(d.get('error_500_samples', []))}",
        "\n_Fix:_ Investigate server logs for PHP/application errors on affected URLs.\n",
        "### 2.2 Redirects\n",
        f"**Redirect chains (> 2 hops):** {d.get('chain_issues', 0):,} — Severity: **Medium**\n",
        "### 2.3 Canonical Tags\n",
        f"**Missing canonical:** {d['missing_canon']:,} ({pct(d['missing_canon'])}) — Severity: **High**",
        "\n_Fix:_ Enable canonical output in your CMS meta module.\n",
        f"**Canonical conflict (node/NNN):** {d.get('canon_conflict', 0):,} — Severity: **High**",
        "\n_Fix:_ Ensure CMS uses the clean URL alias in canonical tag output.\n",
        "---\n",
        "## 3. Images\n",
        f"**Pages with missing alt text:** {d['img_alt_pages']:,} ({pct(d['img_alt_pages'])}) — Severity: **High** (ADA/WCAG violation)",
        f"\n**Total images missing alt:** {d.get('total_imgs_no_alt', 0):,}",
        "\n_Fix:_ Make alt text required on all image fields. Bulk-update existing content.\n",
        "---\n",
        "## 4. Crawl Budget & Sitemap\n",
        "See `crawl_budget_analysis.csv` for full metrics.\n",
        "---\n",
        "## 5. Findability\n",
        f"**Orphan pages (0 inbound links):** {d.get('orphan_count', 'N/A')}",
        f"\n**Average click depth from homepage:** {d.get('avg_depth', 'N/A')}",
        f"\n**BreadcrumbList schema coverage:** {d.get('breadcrumb_pct', '0%')}\n",
    ]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def write_geo_findings(d: dict, out_dir: str, audit_date: str) -> None:
    geo = d.get("geo_detail", {})
    path = os.path.join(out_dir, "reports", "02_geo_findings.md")
    gs = d.get("geo_sample_total", 0) or 1

    def gpct(n): return f"{100*n//gs}%" if gs else "0%"

    lines = [
        f"# {d['client']} — GEO Findings\n",
        f"**Audit Date:** {audit_date} | **GEO sample:** {d.get('geo_sample_total', 0):,} URLs\n",
        "---\n",
        "## 1. Structured Data Coverage\n",
        f"**Pages with any schema:** {geo.get('has_any_schema', 0):,} of {gs:,} ({gpct(geo.get('has_any_schema', 0))})\n",
        "### Entity Type Coverage\n",
        "| Entity Type | Pages With Schema | Coverage |",
        "|---|---|---|",
    ]
    for etype in ["Organization", "Person", "Article/NewsArticle", "Event", "FAQPage",
                  "HowTo", "BreadcrumbList", "WebPage", "VideoObject",
                  "JobPosting", "SpeakableSpecification"]:
        field_key = etype.lower().replace("/", "_").replace(" ", "_")
        count = geo.get(f"has_{field_key}", 0)
        lines.append(f"| {etype} | {count:,} | {gpct(count)} |")

    lines += [
        "",
        "## 2. AI Crawlability\n",
        f"**llms.txt:** {'Present' if d.get('llms_present') else 'Absent (404)'} — "
        f"{'GEO gap: no AI-readable site summary' if not d.get('llms_present') else 'Present'}",
        f"\n**AI bots blocked in robots.txt:** {d.get('blocked_ai_bots', 'None detected')}",
        "\n_Recommendation:_ Allow GPTBot, ClaudeBot, PerplexityBot for AI answer engine visibility.\n",
        "## 3. E-E-A-T Signals\n",
        f"**Author byline markup:** {geo.get('has_byline', 0):,} pages ({gpct(geo.get('has_byline', 0))})",
        f"\n**Publication date markup:** {geo.get('has_date_published', 0):,} pages ({gpct(geo.get('has_date_published', 0))})\n",
        "## 4. FAQ Schema Opportunities\n",
        f"**Pages with FAQ patterns but no FAQPage schema:** {d.get('faq_opportunities', 0):,}",
        "\n_Impact:_ Missed FAQ rich results and AI Q&A extraction opportunities.\n",
        "## 5. Consequence of No Action\n",
        "As AI answer engines (ChatGPT, Perplexity, Google AI Overviews) become primary discovery "
        "surfaces, sites without structured data and AI-accessible content become invisible. "
        "Competitors with proper schema markup and llms.txt will be cited; this site will not.",
    ]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def write_geo_scorecard(d: dict, out_dir: str, audit_date: str) -> None:
    geo = d.get("geo_score", {})
    path = os.path.join(out_dir, "reports", "03_geo_scorecard.md")
    lines = [
        f"# {d['client']} — GEO Readiness Scorecard\n",
        f"**Audit Date:** {audit_date}\n",
        "| Dimension | Score | Evidence Summary |",
        "|---|---|---|",
        f"| Structured Data Coverage | {geo.get('structured_data', 0)}/10 | {d.get('geo_schema_pct', '0%')} of sampled pages have schema |",
        f"| Entity Relationship Clarity | {geo.get('entity_clarity', 0)}/10 | Organization @id established: {d.get('entity_id_present', False)} |",
        f"| AI Crawlability | {geo.get('ai_crawlability', 0)}/10 | llms.txt: {'Present' if d.get('llms_present') else 'Absent'} |",
        f"| E-E-A-T Signal Strength | {geo.get('eeat', 0)}/10 | Author markup: {d.get('byline_pct', '0%')} |",
        f"| Content Depth & Citability | {geo.get('citability', 0)}/10 | FAQ schema opportunities: {d.get('faq_opportunities', 0):,} |",
        f"| Search & Findability | {geo.get('findability', 0)}/10 | BreadcrumbList: {d.get('breadcrumb_pct', '0%')} |",
        f"| **OVERALL GEO READINESS** | **{geo.get('overall', 0)}/10** | |",
        "",
        "## Priority GEO Fixes by Score Impact\n",
        "| Fix | Score Impact |",
        "|---|---|",
        "| Implement BreadcrumbList sitewide | +1.5 pts |",
        "| Establish Organization @id + sameAs | +1.5 pts |",
        "| Create llms.txt | +1.0 pt |",
        "| Allow AI crawlers (robots.txt / WAF) | +2.0 pts |",
        "| Add Article schema to editorial content | +1.0 pt |",
        "| Add FAQPage schema to help content | +1.0 pt |",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def build_recommendations(d: dict) -> list[dict]:
    recs = []
    t = d["total_200"] or 1

    def _add(rank, cat, title, sev, affected, effort, impact, impl, consequence):
        recs.append(dict(
            priority_rank=rank, category=cat, issue_title=title, severity=sev,
            affected_url_count=affected, effort=effort, impact=impact,
            implementation_notes=impl, consequence_of_no_action=consequence,
        ))

    _add(1, "SEO", f"Meta descriptions missing on {d['missing_desc']:,} pages ({100*d['missing_desc']//t}%)",
         "Critical", d["missing_desc"], "Medium", "High",
         f"Configure {d.get('cms','CMS')} meta description token to generate from body summary/teaser.",
         "Google auto-generates low-quality snippets. Organic CTR depressed across most of the site.")
    _add(2, "SEO", f"Duplicate title tags on {d['dup_titles']:,} pages",
         "Critical", d["dup_titles"], "Medium", "High",
         "Audit meta title token — must produce unique per-page output.",
         "Pages treated as duplicates. Rankings diluted.")
    if d["errors_5xx"] > 0:
        _add(3, "SEO", f"{d['errors_5xx']:,} server errors (5xx)",
             "Critical", d["errors_5xx"], "Medium", "High",
             "Check server logs for PHP/application errors on affected URLs.",
             "Crawl frequency reduction. Pages de-indexed over time.")
    if d["errors_4xx"] > 0:
        _add(4, "SEO", f"{d['errors_4xx']:,} client errors (4xx)",
             "High", d["errors_4xx"], "Medium", "High",
             "Implement 301 redirects or remove from sitemap.",
             "Crawl budget waste. Sitemaps listing 404s signal poor hygiene.")
    _add(5, "SEO", f"Missing canonical tags on {d['missing_canon']:,} pages",
         "High", d["missing_canon"], "Low", "Medium",
         "Enable canonical output in CMS meta module.",
         "Duplicate content signals. Google picks unintended canonical.")
    _add(6, "SEO", f"Images missing alt text on {d['img_alt_pages']:,} pages",
         "High", d["img_alt_pages"], "High", "High",
         "Make alt text required on all image fields. Bulk update existing content.",
         "ADA/WCAG non-compliance. Legal exposure. Image SEO signals lost.")
    _add(7, "SEO", f"Missing H1 on {d['missing_h1']:,} pages",
         "High", d["missing_h1"], "Medium", "Medium",
         "Audit page templates. Ensure content title renders as <h1>.",
         "No primary topical signal. Pages harder to rank for primary intent.")
    if d.get("geo"):
        gs = d.get("geo_sample_total", 1) or 1
        geo_d = d.get("geo_detail", {})
        bc = geo_d.get("has_breadcrumb_schema", 0)
        _add(8, "GEO", f"BreadcrumbList schema absent on {gs - bc:,} pages",
             "Critical", gs - bc, "Low", "High",
             "Install schema_metatag or equivalent. Map path hierarchy to BreadcrumbList.",
             "No breadcrumb rich results. AI models lack site hierarchy understanding.")
        org = geo_d.get("has_organization_schema", 0)
        _add(9, "GEO", f"Organization schema absent on {gs - org:,} pages",
             "High", gs - org, "Low", "High",
             "Add sitewide Organization JSON-LD block with @id, sameAs, contactPoint.",
             "AI models cannot anchor entity relationships to this organization.")
        if not d.get("llms_present"):
            _add(10, "GEO", "llms.txt absent",
                 "High", 0, "Low", "Medium",
                 "Create /llms.txt with org summary, key content sections, citation preference.",
                 "AI systems have no authoritative site summary. Missed GEO signal.")
        if d.get("faq_opportunities", 0) > 0:
            _add(11, "GEO", f"{d['faq_opportunities']:,} FAQ schema opportunities",
                 "High", d["faq_opportunities"], "Medium", "High",
                 "Add FAQPage schema to pages with visible Q&A patterns.",
                 "Missed FAQ rich results. AI Q&A extraction not possible.")

    return recs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = build_parser().parse_args()

    if not args.url and not args.input_dir:
        sys.exit("ERROR: provide --url or --input")

    out_dir = os.path.expanduser(args.output)
    csv_dir = os.path.join(out_dir, "csv")
    rep_dir = os.path.join(out_dir, "reports")
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(rep_dir, exist_ok=True)

    session = make_session(args)
    base_url = args.url or ""
    audit_date = datetime.now(timezone.utc).strftime("%B %d, %Y")

    # --- URL loading ---------------------------------------------------------
    if args.input_dir:
        print(f"Loading URLs from existing crawl: {args.input_dir}")
        urls = load_urls_from_input(args.input_dir)
        if base_url and not urls:
            sys.exit(f"No URLs found in {args.input_dir}")
        if not base_url and urls:
            base_url = urlparse(urls[0]).scheme + "://" + urlparse(urls[0]).netloc
    else:
        if args.url:
            try:
                resp = session.get(args.url, timeout=10)
                if resp.status_code not in (200, 301, 302):
                    sys.exit(f"Site not reachable: {args.url} -> {resp.status_code}")
            except Exception as exc:
                sys.exit(f"Cannot reach {args.url}: {exc}")
        print(f"Discovering URLs from {base_url}")
        urls = discover_urls_from_sitemap(base_url, session, args)
        if not urls:
            sys.exit(f"No URLs discovered. Try --sitemap or --no-sitemap with --url.")
    print(f"URLs to audit: {len(urls):,}\n")

    # --- SEO crawl -----------------------------------------------------------
    print(f"Running SEO crawl (concurrency={args.concurrency})...")
    all_rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(crawl_url, u, session, args.timeout): u for u in urls}
        for fut in tqdm(as_completed(futures), total=len(futures), unit="url"):
            all_rows.append(fut.result())

    statuses = Counter(str(r["http_status"]) for r in all_rows)
    total_200 = statuses.get("200", 0)
    print(f"\nCrawl done: {len(all_rows):,} URLs | 200: {total_200:,} | "
          f"4xx: {sum(v for k, v in statuses.items() if k.startswith('4')):,} | "
          f"5xx: {sum(v for k, v in statuses.items() if k.startswith('5')):,}")

    # Duplicate detection
    title_map: dict[str, list[str]] = defaultdict(list)
    desc_map: dict[str, list[str]] = defaultdict(list)
    for r in all_rows:
        if r.get("title_tag"):
            title_map[r["title_tag"].strip()].append(r["url"])
        if r.get("meta_description"):
            desc_map[r["meta_description"].strip()].append(r["url"])
    dup_title_set = {t for t, urls_ in title_map.items() if len(urls_) >= 2}
    dup_desc_set = {d for d, urls_ in desc_map.items() if len(urls_) >= 2}
    for r in all_rows:
        r["title_duplicate_flag"] = r.get("title_tag", "").strip() in dup_title_set
        r["meta_description_duplicate_flag"] = r.get("meta_description", "").strip() in dup_desc_set

    # Write SEO CSVs
    fields = [
        "url", "http_status", "redirect_target", "redirect_chain_length",
        "title_tag", "title_length", "title_missing", "title_duplicate_flag",
        "meta_description", "meta_description_length", "meta_description_missing",
        "meta_description_duplicate_flag", "canonical_url", "canonical_is_self",
        "canonical_missing", "canonical_conflict", "meta_robots", "x_robots_tag",
        "h1_text", "h1_count", "h1_missing", "h2_count", "h3_count", "word_count",
        "image_count", "images_missing_alt", "images_with_empty_alt",
        "internal_link_count", "external_link_count",
        "has_og_title", "has_og_description", "has_og_image", "has_twitter_card",
        "schema_types_present", "schema_count", "response_time_ms",
        "has_noindex", "has_nofollow_page", "content_type",
        "last_modified_header", "page_size_bytes",
    ]

    def _write_csv(path, fieldnames, rows):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    _write_csv(os.path.join(csv_dir, "seo_crawl_raw.csv"), fields, all_rows)

    error_rows = [{"url": r["url"], "http_status": r["http_status"]}
                  for r in all_rows if str(r.get("http_status", "")).startswith(("4", "5"))]
    _write_csv(os.path.join(csv_dir, "seo_errors.csv"), ["url", "http_status"], error_rows)

    redirect_rows = [{"url": r["url"], "http_status": r["http_status"],
                      "redirect_target": r["redirect_target"],
                      "redirect_chain_length": r["redirect_chain_length"],
                      "chain_issue": r["redirect_chain_length"] > 2}
                     for r in all_rows if r.get("redirect_chain_length", 0) > 0]
    _write_csv(os.path.join(csv_dir, "seo_redirects.csv"),
               ["url", "http_status", "redirect_target", "redirect_chain_length", "chain_issue"],
               redirect_rows)

    dup_title_rows = [{"title_tag": t, "affected_url_count": len(u_list),
                       "urls": " | ".join(u_list[:15])}
                      for t, u_list in sorted(title_map.items(), key=lambda x: -len(x[1]))
                      if len(u_list) >= 2]
    _write_csv(os.path.join(csv_dir, "seo_duplicate_titles.csv"),
               ["title_tag", "affected_url_count", "urls"], dup_title_rows)

    dup_meta_rows = [{"meta_description": d, "affected_url_count": len(u_list),
                      "urls": " | ".join(u_list[:15])}
                     for d, u_list in sorted(desc_map.items(), key=lambda x: -len(x[1]))
                     if len(u_list) >= 2]
    _write_csv(os.path.join(csv_dir, "seo_duplicate_meta.csv"),
               ["meta_description", "affected_url_count", "urls"], dup_meta_rows)

    img_rows = [{"url": r["url"], "image_count": r["image_count"],
                 "images_missing_alt": r["images_missing_alt"]}
                for r in all_rows if r.get("images_missing_alt", 0) > 0]
    _write_csv(os.path.join(csv_dir, "seo_images_no_alt.csv"),
               ["url", "image_count", "images_missing_alt"], img_rows)

    # Aggregate metrics
    missing_title = sum(1 for r in all_rows if r.get("title_missing") is True)
    missing_desc = sum(1 for r in all_rows if r.get("meta_description_missing") is True)
    missing_h1 = sum(1 for r in all_rows if r.get("h1_missing") is True)
    missing_canon = sum(1 for r in all_rows if r.get("canonical_missing") is True)
    canon_conflict = sum(1 for r in all_rows if r.get("canonical_conflict") is True)
    errors_4xx = sum(v for k, v in statuses.items() if k.startswith("4"))
    errors_5xx = sum(v for k, v in statuses.items() if k.startswith("5"))
    img_alt_pages = len(img_rows)
    total_imgs_no_alt = sum(r.get("images_missing_alt", 0) for r in all_rows)
    chain_issues = sum(1 for r in redirect_rows if r.get("chain_issue"))
    dup_title_count = sum(1 for r in all_rows if r.get("title_duplicate_flag") is True)
    dup_desc_count = sum(1 for r in all_rows if r.get("meta_description_duplicate_flag") is True)

    # Crawl budget analysis
    robots = check_robots(base_url, session, args.timeout) if base_url else {}
    budget_rows = [
        {"metric": "total_urls_crawled", "value": len(all_rows), "note": ""},
        {"metric": "http_200", "value": total_200, "note": ""},
        {"metric": "http_4xx", "value": errors_4xx, "note": ""},
        {"metric": "http_5xx", "value": errors_5xx, "note": ""},
        {"metric": "robots_has_admin_rule", "value": robots.get("has_admin_rule", "N/A"), "note": ""},
        {"metric": "robots_has_jsonapi_rule", "value": robots.get("has_jsonapi_rule", "N/A"), "note": ""},
        {"metric": "robots_has_pagination_rule", "value": robots.get("has_pagination_rule", "N/A"), "note": ""},
        {"metric": "robots_blocked_ai_bots", "value": robots.get("blocked_ai_bots", "N/A"), "note": ""},
    ]
    _write_csv(os.path.join(csv_dir, "crawl_budget_analysis.csv"),
               ["metric", "value", "note"], budget_rows)

    # Findability (lightweight)
    breadcrumb_count = sum(1 for r in all_rows if "BreadcrumbList" in (r.get("schema_types_present") or ""))
    breadcrumb_pct = f"{100 * breadcrumb_count // total_200}%" if total_200 else "0%"
    find_rows = [
        {"metric": "total_urls_200", "value": total_200, "detail": ""},
        {"metric": "breadcrumb_schema_count", "value": breadcrumb_count, "detail": ""},
        {"metric": "breadcrumb_schema_pct", "value": breadcrumb_pct, "detail": ""},
        {"metric": "orphan_pages", "value": "N/A", "detail": "Run full findability scan with --input for link graph"},
    ]
    _write_csv(os.path.join(csv_dir, "findability_analysis.csv"),
               ["metric", "value", "detail"], find_rows)

    # --- GEO audit -----------------------------------------------------------
    geo_detail: dict = {}
    llms_present = False
    blocked_ai_bots = "Not checked"
    faq_opportunities = 0
    geo_sample_total = 0
    geo_schema_pct = "0%"
    entity_id_present = False
    byline_pct = "0%"

    if args.geo and base_url:
        step = max(1, len(urls) // 5000)
        geo_sample = urls[::step][:5000]
        geo_sample_total = len(geo_sample)
        print(f"\nRunning GEO audit on {geo_sample_total:,} sampled URLs...")

        geo_rows: list[dict] = []
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futures = {ex.submit(geo_audit_url, u, session, args.timeout): u for u in geo_sample}
            for fut in tqdm(as_completed(futures), total=len(futures), unit="url"):
                geo_rows.append(fut.result())

        geo_fields = [
            "url", "http_status", "schema_types_found",
            "has_organization_schema", "has_person_schema", "has_article_schema",
            "has_event_schema", "has_faq_schema", "has_howto_schema",
            "has_breadcrumb_schema", "has_webpage_schema", "has_video_schema",
            "has_jobposting_schema", "has_speakable_schema",
            "entity_id_present", "sameAs_present", "organization_name_consistent",
            "has_og_complete", "has_twitter_card_complete",
            "schema_validation_errors", "modification_date",
            "faq_pattern_no_schema", "js_rendering_risk",
            "has_byline", "has_date_published",
        ]
        _write_csv(os.path.join(csv_dir, "geo_structured_data.csv"), geo_fields, geo_rows)

        # AI signals
        llms = check_llms_txt(base_url, session, args.timeout)
        llms_present = llms["present"]
        blocked_ai_bots = robots.get("blocked_ai_bots", "None detected")

        ai_rows = [
            {"signal": "llms_txt_present", "value": llms_present},
            {"signal": "llms_txt_length", "value": llms.get("length_chars", 0)},
            {"signal": "robots_blocked_ai_bots", "value": blocked_ai_bots},
            {"signal": "robots_has_admin_rule", "value": robots.get("has_admin_rule", "N/A")},
            {"signal": "robots_has_jsonapi_rule", "value": robots.get("has_jsonapi_rule", "N/A")},
        ]
        _write_csv(os.path.join(csv_dir, "geo_ai_crawlability.csv"), ["signal", "value"], ai_rows)

        # Entity summary
        entity_types = ["Organization", "Person", "Article", "Event", "FAQPage",
                        "HowTo", "BreadcrumbList", "WebPage", "VideoObject",
                        "JobPosting", "SpeakableSpecification"]
        entity_summary = []
        for et in entity_types:
            field = f"has_{et.lower()}_schema"
            count = sum(1 for r in geo_rows if r.get(field) is True)
            entity_summary.append({"entity_type": et, "pages_with_schema": count,
                                   "sample_total": geo_sample_total,
                                   "coverage_pct": f"{100*count//geo_sample_total}%"})
            geo_detail[field] = count
        _write_csv(os.path.join(csv_dir, "geo_entity_relationships.csv"),
                   ["entity_type", "pages_with_schema", "sample_total", "coverage_pct"],
                   entity_summary)

        # E-E-A-T
        eeat_rows = [{"url": r["url"], "has_byline": r.get("has_byline"),
                      "has_date_published": r.get("has_date_published"),
                      "has_organization_schema": r.get("has_organization_schema")}
                     for r in geo_rows]
        _write_csv(os.path.join(csv_dir, "geo_eeat_signals.csv"),
                   ["url", "has_byline", "has_date_published", "has_organization_schema"],
                   eeat_rows)

        # FAQ opportunities
        faq_rows = [{"url": r["url"]} for r in geo_rows if r.get("faq_pattern_no_schema")]
        _write_csv(os.path.join(csv_dir, "geo_faq_opportunities.csv"), ["url"], faq_rows)

        # Aggregate GEO metrics
        has_any = sum(1 for r in geo_rows if r.get("schema_types_found"))
        has_byline = sum(1 for r in geo_rows if r.get("has_byline"))
        has_date = sum(1 for r in geo_rows if r.get("has_date_published"))
        faq_opportunities = len(faq_rows)
        entity_id_present = any(r.get("entity_id_present") for r in geo_rows)
        geo_schema_pct = f"{100*has_any//geo_sample_total}%"
        byline_pct = f"{100*has_byline//geo_sample_total}%"
        geo_detail.update(has_any_schema=has_any, has_byline=has_byline,
                          has_date_published=has_date)

        # GEO scoring
        schema_score = min(10, int(10 * has_any / geo_sample_total * 2))
        org = geo_detail.get("has_organization_schema", 0)
        entity_score = min(10, int(10 * org / geo_sample_total * 3))
        ai_score = (3 if llms_present else 0) + (3 if blocked_ai_bots == "None detected" else 0) + 2
        eeat_score = min(10, int((has_byline + has_date) / (geo_sample_total * 2) * 20))
        bc = geo_detail.get("has_breadcrumb_schema", 0)
        citability_score = min(10, 5 + (3 if faq_opportunities < 10 else 0) + (2 if bc > 0 else 0))
        find_score = min(10, 4 + (3 if bc > 0 else 0) + (3 if breadcrumb_count > 0 else 0))
        overall = int((schema_score + entity_score + ai_score + eeat_score + citability_score + find_score) / 6)
        geo_score = dict(structured_data=schema_score, entity_clarity=entity_score,
                         ai_crawlability=ai_score, eeat=eeat_score,
                         citability=citability_score, findability=find_score, overall=overall)

    else:
        geo_score = {}

    # --- Recommendations -----------------------------------------------------
    seo_score = compute_seo_score(
        total_200, missing_title, dup_title_count, missing_desc, dup_desc_count,
        missing_h1, errors_4xx, errors_5xx, missing_canon, canon_conflict,
        img_alt_pages, errors_5xx > 50 or errors_4xx > 200,
    )

    data = dict(
        client=args.client, company=args.company, base_url=base_url,
        cms=args.cms, total=len(all_rows), total_200=total_200,
        missing_title=missing_title, missing_desc=missing_desc,
        missing_h1=missing_h1, missing_canon=missing_canon,
        canon_conflict=canon_conflict, errors_4xx=errors_4xx, errors_5xx=errors_5xx,
        img_alt_pages=img_alt_pages, total_imgs_no_alt=total_imgs_no_alt,
        dup_titles=dup_title_count, dup_descs=dup_desc_count,
        chain_issues=chain_issues, crawl_budget_critical=(errors_5xx > 50 or errors_4xx > 200),
        seo_score=seo_score, breadcrumb_pct=breadcrumb_pct,
        orphan_count="N/A", avg_depth="N/A",
        geo=args.geo, geo_detail=geo_detail, geo_score=geo_score if args.geo else {},
        geo_sample_total=geo_sample_total, geo_schema_pct=geo_schema_pct,
        llms_present=llms_present, blocked_ai_bots=blocked_ai_bots,
        faq_opportunities=faq_opportunities, entity_id_present=entity_id_present,
        byline_pct=byline_pct,
        missing_title_samples=[r["url"] for r in all_rows if r.get("title_missing") is True][:5],
        missing_desc_samples=[r["url"] for r in all_rows if r.get("meta_description_missing") is True][:5],
        error_404_samples=[r["url"] for r in error_rows if str(r.get("http_status")) == "404"][:5],
        error_500_samples=[r["url"] for r in error_rows if str(r.get("http_status")) == "500"][:5],
        short_titles=sum(1 for r in all_rows if r.get("title_tag") and int(r.get("title_length") or 0) < 30),
        long_titles=sum(1 for r in all_rows if int(r.get("title_length") or 0) > 60),
    )
    recs = build_recommendations(data)
    data["recommendations"] = recs

    rec_fields = ["priority_rank", "category", "issue_title", "severity",
                  "affected_url_count", "effort", "impact",
                  "implementation_notes", "consequence_of_no_action"]
    _write_csv(os.path.join(csv_dir, "recommendations.csv"), rec_fields, recs)

    # --- Reports -------------------------------------------------------------
    write_executive_summary(data, out_dir, audit_date)
    write_seo_findings(data, out_dir, audit_date)
    if args.geo:
        write_geo_findings(data, out_dir, audit_date)
        write_geo_scorecard(data, out_dir, audit_date)

    # --- Summary -------------------------------------------------------------
    print(f"\n=== SEO Audit Complete ===")
    print(f"  Client        : {args.client}")
    print(f"  URL           : {base_url}")
    print(f"  Pages audited : {len(all_rows):,}")
    print(f"  SEO Score     : {seo_score['total']}/100")
    if args.geo:
        print(f"  GEO Score     : {geo_score.get('overall', 0)}/10")
    print(f"  Output        : {out_dir}")
    print(f"\nCSV files:")
    for fname in os.listdir(csv_dir):
        fpath = os.path.join(csv_dir, fname)
        rows = sum(1 for _ in open(fpath, encoding="utf-8")) - 1
        print(f"  {fname}: {rows:,} rows")
    print(f"\nReports:")
    for fname in sorted(os.listdir(rep_dir)):
        fpath = os.path.join(rep_dir, fname)
        print(f"  {fname}: {os.path.getsize(fpath):,} bytes")

    if args.pptx:
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        pptx_script = os.path.join(os.path.dirname(skill_dir), "audit-pptx", "generate_audit_pptx.py")
        if os.path.exists(pptx_script):
            import subprocess
            pptx_args = [sys.executable, pptx_script,
                         "--input", out_dir,
                         "--client", args.client,
                         "--company", args.company,
                         "--brand-color", args.brand_color]
            subprocess.run(pptx_args, check=False)
        else:
            print("\nNote: --pptx flag set but audit-pptx skill not found. Run /audit-pptx separately.")


if __name__ == "__main__":
    main()
