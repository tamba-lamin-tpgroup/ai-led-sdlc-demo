"""
Generic Web Crawler for content inventory and SEO data collection.

Supports local (DDEV/localhost) and remote targets. Accepts a sitemap URL,
a local sitemap XML file, or auto-discovers /sitemap.xml. Falls back to
BFS link-following if no sitemap is found or --no-sitemap is passed.

Usage:
    python3 crawler.py --url https://example.com
    python3 crawler.py --url https://mysite.ddev.site --local
    python3 crawler.py --url https://example.com --sitemap /path/to/sitemap.xml
    python3 crawler.py --url https://example.com --max-pages 5000 --output ./out
"""

import argparse
import csv
import json
import logging
import os
import re
import ssl
import sys
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

try:
    from xml.etree import ElementTree as ET
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generic web crawler — produces a content inventory CSV.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--url", required=True, help="Base URL to crawl")
    p.add_argument("--local", action="store_true",
                   help="Local/dev site: disable SSL verification")
    p.add_argument("--sitemap", default=None,
                   help="Sitemap URL or local XML file path")
    p.add_argument("--max-pages", type=int, default=1000,
                   help="Maximum pages to crawl (0 = unlimited)")
    p.add_argument("--output", default="./crawl-output",
                   help="Output directory")
    p.add_argument("--exclude", action="append", default=[],
                   help="Regex URL exclusion pattern (repeatable)")
    p.add_argument("--include", action="append", default=[],
                   help="Only crawl URLs matching this pattern (repeatable)")
    p.add_argument("--scope", default=None,
                   help="Restrict to path prefix (e.g. /news)")
    p.add_argument("--concurrency", type=int, default=5,
                   help="Parallel worker count")
    p.add_argument("--timeout", type=int, default=15,
                   help="Per-request timeout in seconds")
    p.add_argument("--depth", type=int, default=10,
                   help="Max BFS crawl depth")
    p.add_argument("--delay", type=int, default=0,
                   help="Delay between requests in milliseconds")
    p.add_argument("--user-agent", default="SEO-Audit-Bot/1.0 (content-inventory; not-indexing)",
                   help="HTTP User-Agent string")
    p.add_argument("--screenshots", action="store_true",
                   help="Capture full-page screenshots (requires Playwright)")
    p.add_argument("--no-sitemap", action="store_true",
                   help="Skip sitemap discovery, use BFS link-following only")
    return p


# ---------------------------------------------------------------------------
# HTTP session setup
# ---------------------------------------------------------------------------

def make_session(args: argparse.Namespace) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": args.user_agent})
    if args.local:
        import urllib3
        urllib3.disable_warnings()
        session.verify = False
    return session


# ---------------------------------------------------------------------------
# URL utilities
# ---------------------------------------------------------------------------

def normalize_url(url: str) -> str:
    """Strip fragment, sort query params, normalise trailing slash."""
    p = urlparse(url)
    path = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme, p.netloc, path, p.params, p.query, ""))


def same_host(url: str, base_host: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc == base_host or not parsed.netloc


def is_excluded(url: str, exclude_patterns: list[str],
                include_patterns: list[str], scope: str | None,
                base_host: str) -> bool:
    """Return True if the URL should be skipped."""
    if not same_host(url, base_host):
        return True
    path = urlparse(url).path
    for pat in exclude_patterns:
        if re.search(pat, url):
            return True
    if include_patterns and not any(re.search(p, url) for p in include_patterns):
        return True
    if scope and not path.startswith(scope):
        return True
    return False


# ---------------------------------------------------------------------------
# Sitemap parsing
# ---------------------------------------------------------------------------

SM_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def _parse_sitemap_xml(xml_bytes: bytes) -> tuple[list[str], list[dict]]:
    """Return (child_sitemap_urls, url_entries) from an XML document."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return [], []
    # Sitemap index
    child_sitemaps = [
        el.text.strip()
        for el in root.findall(".//sm:sitemap/sm:loc", SM_NS)
        if el.text
    ] or [
        el.text.strip()
        for el in root.findall(".//sitemap/loc")
        if el.text
    ]
    # URL set
    entries = []
    for url_el in root.findall(".//sm:url", SM_NS) or root.findall(".//url"):
        loc = (url_el.findtext("sm:loc", namespaces=SM_NS) or
               url_el.findtext("loc") or "").strip()
        if loc:
            entries.append({
                "url": loc,
                "lastmod": url_el.findtext("sm:lastmod", default="", namespaces=SM_NS) or "",
                "priority": url_el.findtext("sm:priority", default="", namespaces=SM_NS) or "",
            })
    return child_sitemaps, entries


def fetch_sitemap_urls(sitemap_source: str, session: requests.Session,
                       base_host: str) -> list[dict]:
    """
    Fetch and parse a sitemap index or URL set.

    sitemap_source can be a URL or a local file path. Recursively follows
    child sitemaps and detects paginated ?page=N patterns.
    """
    seen_sitemaps: set[str] = set()
    all_entries: list[dict] = []

    def _fetch_raw(source: str) -> bytes | None:
        if os.path.isfile(source):
            with open(source, "rb") as fh:
                return fh.read()
        try:
            resp = session.get(source, timeout=30)
            return resp.content if resp.status_code == 200 else None
        except Exception as exc:
            logging.warning("Sitemap fetch failed for %s: %s", source, exc)
            return None

    def _process(source: str) -> None:
        if source in seen_sitemaps:
            return
        seen_sitemaps.add(source)
        raw = _fetch_raw(source)
        if not raw:
            return
        child_sitemaps, entries = _parse_sitemap_xml(raw)
        if child_sitemaps:
            for child in child_sitemaps:
                # Detect paginated pattern and expand
                if "page=" in child:
                    base_no_page = re.sub(r"[?&]page=\d+", "", child)
                    sep = "?" if "?" not in base_no_page else "&"
                    current_page = int(re.search(r"page=(\d+)", child).group(1))
                    for page in range(current_page, current_page + 100):
                        paged = f"{base_no_page}{sep}page={page}"
                        if paged in seen_sitemaps:
                            continue
                        paged_raw = _fetch_raw(paged)
                        if not paged_raw:
                            break
                        _, paged_entries = _parse_sitemap_xml(paged_raw)
                        if not paged_entries:
                            break
                        seen_sitemaps.add(paged)
                        all_entries.extend(paged_entries)
                        time.sleep(0.1)
                else:
                    _process(child)
        all_entries.extend(entries)

    _process(sitemap_source)
    return all_entries


def rewrite_host(url: str, original_host: str, target_host: str) -> str:
    """Replace the host in a URL (used to remap sitemap entries to local host)."""
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != target_host:
        return parsed._replace(netloc=target_host,
                               scheme=urlparse(f"https://{target_host}").scheme or "https").geturl()
    return url


# ---------------------------------------------------------------------------
# BFS link discovery
# ---------------------------------------------------------------------------

def bfs_discover(seed_url: str, session: requests.Session,
                 args: argparse.Namespace, base_host: str,
                 known_urls: set[str]) -> list[str]:
    """BFS link-follower starting from seed_url."""
    queue: deque[tuple[str, int]] = deque([(seed_url, 0)])
    visited: set[str] = set()
    discovered: list[str] = []
    cap = args.max_pages or 100_000

    logging.info("BFS discovery starting from %s", seed_url)
    while queue and len(discovered) < cap:
        url, depth = queue.popleft()
        norm = normalize_url(url)
        if norm in visited:
            continue
        visited.add(norm)
        if is_excluded(url, args.exclude, args.include, args.scope, base_host):
            continue
        if norm not in known_urls:
            discovered.append(norm)
            known_urls.add(norm)

        if depth >= args.depth:
            continue
        try:
            resp = session.get(url, timeout=args.timeout, allow_redirects=True)
            if resp.status_code == 200 and "text/html" in resp.headers.get("Content-Type", ""):
                soup = BeautifulSoup(resp.text, "lxml")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                        continue
                    abs_url = urljoin(url, href)
                    if same_host(abs_url, base_host):
                        queue.append((abs_url, depth + 1))
        except Exception:
            pass
        if args.delay:
            time.sleep(args.delay / 1000)

    return discovered


# ---------------------------------------------------------------------------
# Page crawling
# ---------------------------------------------------------------------------

def _text(tag) -> str:
    return tag.get_text(separator=" ", strip=True) if tag else ""


def _word_count(soup: BeautifulSoup) -> int:
    body = soup.find("body")
    if not body:
        return 0
    for s in body(["script", "style", "nav", "header", "footer"]):
        s.decompose()
    return len(body.get_text(separator=" ").split())


def _schema_types(soup: BeautifulSoup) -> str:
    types: list[str] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            t = item.get("@type", "")
            if isinstance(t, list):
                types.extend(t)
            elif t:
                types.append(t)
    return ", ".join(sorted(set(types)))


def crawl_single(url: str, session: requests.Session,
                 timeout: int, base_host: str) -> dict:
    """Fetch and parse a single URL, returning a flat SEO metadata dict."""
    row: dict = {
        "url": url, "http_status": None,
        "redirect_target": "", "redirect_chain_length": 0,
        "title": "", "title_length": 0, "title_missing": True,
        "meta_description": "", "meta_description_length": 0,
        "meta_description_missing": True,
        "canonical_url": "", "canonical_missing": True, "canonical_is_self": False,
        "meta_robots": "", "h1_text": "", "h1_count": 0, "h1_missing": True,
        "h2_count": 0, "h3_count": 0, "word_count": 0,
        "image_count": 0, "images_missing_alt": 0,
        "internal_link_count": 0, "external_link_count": 0,
        "has_og_title": False, "has_og_description": False, "has_og_image": False,
        "has_twitter_card": False, "schema_types": "",
        "response_time_ms": 0, "page_size_bytes": 0,
        "content_type": "", "last_modified_header": "",
        "screenshot_path": "",
    }
    try:
        t0 = time.monotonic()
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        elapsed = int((time.monotonic() - t0) * 1000)

        row["http_status"] = resp.status_code
        row["response_time_ms"] = elapsed
        row["content_type"] = resp.headers.get("Content-Type", "")
        row["last_modified_header"] = resp.headers.get("Last-Modified", "")
        row["page_size_bytes"] = len(resp.content)

        if resp.history:
            row["redirect_chain_length"] = len(resp.history)
            row["redirect_target"] = resp.url

        if resp.status_code != 200 or "text/html" not in row["content_type"]:
            return row

        soup = BeautifulSoup(resp.text, "lxml")

        title_tag = soup.find("title")
        title = _text(title_tag)
        row["title"] = title
        row["title_length"] = len(title)
        row["title_missing"] = not bool(title)

        meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        desc = (meta_desc_tag.get("content", "") or "").strip() if meta_desc_tag else ""
        row["meta_description"] = desc
        row["meta_description_length"] = len(desc)
        row["meta_description_missing"] = not bool(desc)

        canon = soup.find("link", rel=lambda r: r and "canonical" in r)
        if canon:
            canon_href = canon.get("href", "").strip()
            row["canonical_url"] = canon_href
            row["canonical_missing"] = False
            pu, pc = urlparse(url), urlparse(canon_href)
            row["canonical_is_self"] = (
                pc.path.rstrip("/") == pu.path.rstrip("/") and
                (not pc.netloc or pc.netloc == pu.netloc)
            )

        robots_tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
        row["meta_robots"] = (robots_tag.get("content", "") or "").lower() if robots_tag else ""

        h1s = soup.find_all("h1")
        row["h1_count"] = len(h1s)
        row["h1_missing"] = not h1s
        row["h1_text"] = _text(h1s[0]) if h1s else ""
        row["h2_count"] = len(soup.find_all("h2"))
        row["h3_count"] = len(soup.find_all("h3"))
        row["word_count"] = _word_count(BeautifulSoup(resp.text, "lxml"))

        imgs = soup.find_all("img")
        row["image_count"] = len(imgs)
        row["images_missing_alt"] = sum(1 for i in imgs if not i.get("alt"))

        internal = external = 0
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "mailto:", "tel:")):
                continue
            abs_href = urljoin(url, href)
            if same_host(abs_href, base_host):
                internal += 1
            else:
                external += 1
        row["internal_link_count"] = internal
        row["external_link_count"] = external

        row["has_og_title"] = bool(soup.find("meta", property="og:title"))
        row["has_og_description"] = bool(soup.find("meta", property="og:description"))
        row["has_og_image"] = bool(soup.find("meta", property="og:image"))
        row["has_twitter_card"] = bool(
            soup.find("meta", attrs={"name": re.compile(r"twitter:card", re.I)})
        )
        row["schema_types"] = _schema_types(soup)

    except requests.Timeout:
        row["http_status"] = "TIMEOUT"
    except requests.ConnectionError as exc:
        row["http_status"] = f"CONN_ERROR"
    except Exception as exc:
        row["http_status"] = f"ERROR"
        logging.debug("Error crawling %s: %s", url, exc)

    return row


# ---------------------------------------------------------------------------
# Screenshot capture
# ---------------------------------------------------------------------------

def capture_screenshot(url: str, output_dir: str) -> str:
    """Capture a full-page screenshot with Playwright. Returns file path or ''."""
    try:
        from playwright.sync_api import sync_playwright
        fname = re.sub(r"[^\w\-]", "_", urlparse(url).path.strip("/") or "home") + ".png"
        fpath = os.path.join(output_dir, fname)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.screenshot(path=fpath, full_page=True)
            browser.close()
        return fpath
    except Exception as exc:
        logging.warning("Screenshot failed for %s: %s", url, exc)
        return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

INVENTORY_FIELDS = [
    "url", "http_status", "redirect_target", "redirect_chain_length",
    "title", "title_length", "title_missing",
    "meta_description", "meta_description_length", "meta_description_missing",
    "canonical_url", "canonical_missing", "canonical_is_self",
    "meta_robots", "h1_text", "h1_count", "h1_missing",
    "h2_count", "h3_count", "word_count",
    "image_count", "images_missing_alt",
    "internal_link_count", "external_link_count",
    "has_og_title", "has_og_description", "has_og_image", "has_twitter_card",
    "schema_types", "response_time_ms", "page_size_bytes",
    "content_type", "last_modified_header", "screenshot_path",
]


def main() -> None:
    args = build_arg_parser().parse_args()

    out_dir = os.path.expanduser(args.output)
    os.makedirs(out_dir, exist_ok=True)
    if args.screenshots:
        os.makedirs(os.path.join(out_dir, "screenshots"), exist_ok=True)

    log_path = os.path.join(out_dir, "crawl-log.txt")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )

    parsed_base = urlparse(args.url)
    base_host = parsed_base.netloc
    audit_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    logging.info("Crawl started — target: %s — date: %s", args.url, audit_date)

    session = make_session(args)

    # --- Verify reachability -------------------------------------------------
    try:
        check = session.get(args.url, timeout=10, allow_redirects=True)
        if check.status_code not in (200, 301, 302):
            sys.exit(f"ERROR: {args.url} returned {check.status_code}. Is the site up?")
    except Exception as exc:
        sys.exit(f"ERROR: Cannot reach {args.url}: {exc}")
    logging.info("Site is reachable (HTTP %s)", check.status_code)

    # --- URL discovery -------------------------------------------------------
    discovered_urls: list[str] = []
    sitemap_entries: list[dict] = []

    if not args.no_sitemap:
        sitemap_source = args.sitemap
        if not sitemap_source:
            # Auto-detect from robots.txt or default path
            robots_text = ""
            try:
                r = session.get(urljoin(args.url, "/robots.txt"), timeout=10)
                if r.status_code == 200:
                    robots_text = r.text
            except Exception:
                pass
            sitemap_match = re.search(r"^Sitemap:\s*(.+)$", robots_text, re.M | re.I)
            sitemap_source = sitemap_match.group(1).strip() if sitemap_match else urljoin(args.url, "/sitemap.xml")

        logging.info("Fetching sitemap: %s", sitemap_source)
        sitemap_entries = fetch_sitemap_urls(sitemap_source, session, base_host)
        logging.info("Sitemap yielded %d entries", len(sitemap_entries))

        for entry in sitemap_entries:
            url = entry["url"]
            # Rewrite host if sitemap entries point to a different host than target
            if base_host not in url:
                url = rewrite_host(url, urlparse(url).netloc, base_host)
            if not is_excluded(url, args.exclude, args.include, args.scope, base_host):
                discovered_urls.append(url)

        # Save sitemap URL list
        sitemap_path = os.path.join(out_dir, "sitemap-urls.txt")
        with open(sitemap_path, "w", encoding="utf-8") as fh:
            for u in discovered_urls:
                fh.write(u + "\n")

    # BFS supplement if sitemap is missing or short
    bfs_needed = not discovered_urls or (
        args.max_pages and len(discovered_urls) < min(args.max_pages // 2, 100)
    )
    if args.no_sitemap or bfs_needed:
        logging.info("Running BFS link discovery from %s", args.url)
        known = set(discovered_urls)
        bfs_urls = bfs_discover(args.url, session, args, base_host, known)
        discovered_urls.extend(bfs_urls)
        logging.info("BFS added %d URLs (total: %d)", len(bfs_urls), len(discovered_urls))

    # Deduplicate and cap
    seen: set[str] = set()
    clean_urls: list[str] = []
    for u in discovered_urls:
        norm = normalize_url(u)
        if norm not in seen:
            seen.add(norm)
            clean_urls.append(norm)

    cap = args.max_pages or len(clean_urls)
    if len(clean_urls) > cap:
        # Intelligent sample: keep priority sections, sample rest
        priority_prefixes = ("/news", "/blog", "/products", "/services",
                             "/about", "/contact", "/pricing", "/help", "/docs")
        priority = [u for u in clean_urls if any(urlparse(u).path.startswith(p) for p in priority_prefixes)]
        others = [u for u in clean_urls if u not in set(priority)]
        slots = cap - len(priority)
        step = max(1, len(others) // slots) if slots > 0 else 1
        sampled = others[::step][:max(0, slots)]
        clean_urls = priority + sampled
        logging.info("Capped to %d URLs (%d priority + %d sampled)", len(clean_urls), len(priority), len(sampled))

    # Save final crawl list
    crawl_list_path = os.path.join(out_dir, "urls-to-crawl.txt")
    with open(crawl_list_path, "w", encoding="utf-8") as fh:
        for u in clean_urls:
            fh.write(u + "\n")
    logging.info("Final crawl list: %d URLs", len(clean_urls))

    # --- Crawl ---------------------------------------------------------------
    logging.info("Starting crawl with concurrency=%d, timeout=%ds", args.concurrency, args.timeout)
    all_rows: list[dict] = []
    redirect_rows: list[dict] = []
    error_rows: list[dict] = []
    link_map: dict[str, list[str]] = {}

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {executor.submit(crawl_single, url, session, args.timeout, base_host): url
                   for url in clean_urls}
        for future in tqdm(as_completed(futures), total=len(futures), unit="url", desc="Crawling"):
            row = future.result()
            all_rows.append(row)

            if row["redirect_chain_length"] > 0:
                redirect_rows.append({
                    "url": row["url"],
                    "http_status": row["http_status"],
                    "redirect_target": row["redirect_target"],
                    "redirect_chain_length": row["redirect_chain_length"],
                    "chain_issue": row["redirect_chain_length"] > 2,
                })

            status = str(row["http_status"])
            if status.startswith("4") or status.startswith("5"):
                error_rows.append({"url": row["url"], "http_status": row["http_status"]})

            if args.delay:
                time.sleep(args.delay / 1000)

    # Screenshots (sequential — Playwright doesn't play well with threads)
    if args.screenshots:
        logging.info("Capturing screenshots for up to 200 pages...")
        ss_dir = os.path.join(out_dir, "screenshots")
        ss_urls = [r["url"] for r in all_rows if str(r.get("http_status")) == "200"][:200]
        for row in tqdm(all_rows, desc="Screenshots"):
            if row["url"] in ss_urls:
                row["screenshot_path"] = capture_screenshot(row["url"], ss_dir)

    # --- Write outputs -------------------------------------------------------
    inventory_path = os.path.join(out_dir, "inventory.csv")
    with open(inventory_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=INVENTORY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    redirects_path = os.path.join(out_dir, "redirects.csv")
    with open(redirects_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["url", "http_status", "redirect_target", "redirect_chain_length", "chain_issue"])
        writer.writeheader()
        writer.writerows(redirect_rows)

    errors_path = os.path.join(out_dir, "errors.csv")
    with open(errors_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["url", "http_status"])
        writer.writeheader()
        writer.writerows(error_rows)

    from collections import Counter
    statuses = Counter(str(r["http_status"]) for r in all_rows)
    logging.info("Crawl complete — %d URLs processed", len(all_rows))
    logging.info("Status distribution: %s",
                 ", ".join(f"{k}: {v}" for k, v in sorted(statuses.items())))
    logging.info("Outputs written to: %s", out_dir)

    print(f"\n=== Crawl Summary ===")
    print(f"  Target URL     : {args.url}")
    print(f"  URLs crawled   : {len(all_rows):,}")
    print(f"  HTTP 200       : {statuses.get('200', 0):,}")
    print(f"  4xx errors     : {sum(v for k, v in statuses.items() if k.startswith('4')):,}")
    print(f"  5xx errors     : {sum(v for k, v in statuses.items() if k.startswith('5')):,}")
    print(f"  Redirects      : {len(redirect_rows):,}")
    print(f"  Output dir     : {out_dir}")
    print(f"\nFiles written:")
    print(f"  inventory.csv      ({len(all_rows):,} rows)")
    print(f"  redirects.csv      ({len(redirect_rows):,} rows)")
    print(f"  errors.csv         ({len(error_rows):,} rows)")
    print(f"  urls-to-crawl.txt  ({len(clean_urls):,} lines)")
    print(f"  crawl-log.txt")


if __name__ == "__main__":
    main()
