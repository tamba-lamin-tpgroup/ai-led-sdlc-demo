"""
geo_audit.py - Generative Engine Optimization (GEO) audit script.

Audits a web property for AI-system discoverability signals: llms.txt presence,
robots.txt AI-crawler directives, Schema.org structured data (Organization,
WebSite, Article, Person), sameAs entity links, and content structure patterns.
Produces a GEO score (0-100) and a markdown checklist report.

Dependencies: pip install requests beautifulsoup4
No other dependencies required.

Usage:
    python3 geo_audit.py --url https://example.com [--pages 5]
        [--output ./geo-output] [--format markdown|json|both] [--cms SLUG]
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime


# ---------------------------------------------------------------------------
# Dependency guard
# ---------------------------------------------------------------------------

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print(
        "ERROR: Missing dependencies. Run: pip install requests beautifulsoup4",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AI_CRAWLERS = [
    "GPTBot",
    "ClaudeBot",
    "PerplexityBot",
    "GoogleBot-Extended",
    "OAI-SearchBot",
    "Diffbot",
    "CCBot",
]

AUTHORITATIVE_SAME_AS_DOMAINS = [
    "wikidata.org",
    "wikipedia.org",
    "linkedin.com/company",
    "crunchbase.com",
    "bloomberg.com",
    "sec.gov",
    "gleif.org",
]

ENTITY_SCHEMAS = {"Organization", "WebSite", "WebPage", "Article", "NewsArticle", "Person"}
ANSWER_SCHEMAS = {"FAQPage", "HowTo", "QAPage", "speakable"}
PRODUCT_SCHEMAS = {"Product", "Review", "AggregateRating", "Event"}

QUESTION_PREFIXES = re.compile(
    r"^(who|what|when|where|why|how|is|are|can|does|do|will|was|were|has|have)\b",
    re.IGNORECASE,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GEOAuditBot/1.0; +https://github.com/anthropic)"
    )
}

REQUEST_TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 0.5


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def fetch(url: str, timeout: int = REQUEST_TIMEOUT) -> requests.Response | None:
    """Fetch a URL; return Response or None on error."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return resp
    except requests.RequestException as exc:
        print(f"  WARN: fetch failed for {url}: {exc}", file=sys.stderr)
        return None


def fetch_text(url: str) -> str | None:
    """Return response body as text or None."""
    resp = fetch(url)
    if resp is not None and resp.status_code == 200:
        return resp.text
    return None


# ---------------------------------------------------------------------------
# robots.txt analysis
# ---------------------------------------------------------------------------

def audit_robots(base_url: str) -> dict:
    """Parse robots.txt and check for AI-crawler directives."""
    robots_url = urllib.parse.urljoin(base_url, "/robots.txt")
    text = fetch_text(robots_url)

    result = {
        "present": text is not None,
        "crawlers": {},
        "llms_txt_declared": False,
    }

    if text is None:
        return result

    # Detect Sitemap: /llms.txt declaration (some sites add it)
    if "llms.txt" in text:
        result["llms_txt_declared"] = True

    # Simple robots.txt parser: collect Allow/Disallow per user-agent
    current_agents: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            # If we see a new agent start after non-empty current_agents
            # without seeing rules, keep accumulating
            current_agents.append(value)
        elif key in ("allow", "disallow"):
            for agent in current_agents:
                if agent not in result["crawlers"]:
                    result["crawlers"][agent] = {"allow": [], "disallow": []}
                result["crawlers"][agent][key].append(value)
        elif key == "user-agent" or not line:
            current_agents = []

    # Check per-crawler status
    for crawler in AI_CRAWLERS:
        # Look for case-insensitive match
        matched_key = next(
            (k for k in result["crawlers"] if k.lower() == crawler.lower()),
            None,
        )
        if matched_key:
            disallowed = result["crawlers"][matched_key].get("disallow", [])
            # Disallow: / means fully blocked
            blocked = "/" in disallowed or "/*" in disallowed
            result[crawler] = {
                "declared": True,
                "blocked": blocked,
                "disallowed_paths": disallowed,
            }
        else:
            # Check wildcard
            wildcard = result["crawlers"].get("*", {})
            wildcard_disallow = wildcard.get("disallow", [])
            blocked = "/" in wildcard_disallow or "/*" in wildcard_disallow
            result[crawler] = {
                "declared": False,
                "blocked": blocked,
                "disallowed_paths": wildcard_disallow if blocked else [],
            }

    return result


# ---------------------------------------------------------------------------
# llms.txt analysis
# ---------------------------------------------------------------------------

def audit_llms_txt(base_url: str) -> dict:
    """Check for llms.txt at the root and parse basic fields."""
    llms_url = urllib.parse.urljoin(base_url, "/llms.txt")
    resp = fetch(llms_url)

    result = {
        "present": False,
        "url": llms_url,
        "has_description": False,
        "has_preferred_citation": False,
        "has_content_scope": False,
        "has_disallow": False,
        "raw_lines": 0,
    }

    if resp is None or resp.status_code != 200:
        return result

    result["present"] = True
    text = resp.text
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    result["raw_lines"] = len(lines)

    for line in lines:
        lower = line.lower()
        if "description" in lower:
            result["has_description"] = True
        if "citation" in lower or "preferred" in lower:
            result["has_preferred_citation"] = True
        if "scope" in lower or "allow" in lower.replace("disallow", ""):
            result["has_content_scope"] = True
        if "disallow" in lower:
            result["has_disallow"] = True

    return result


# ---------------------------------------------------------------------------
# JSON-LD extraction
# ---------------------------------------------------------------------------

def extract_json_ld(soup: BeautifulSoup) -> list[dict]:
    """Extract all JSON-LD blocks from a page."""
    results = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
            if isinstance(data, list):
                results.extend(data)
            elif isinstance(data, dict):
                results.append(data)
        except (json.JSONDecodeError, TypeError):
            pass
    return results


def collect_schema_types(json_ld_blocks: list[dict]) -> set[str]:
    """Collect all @type values from JSON-LD blocks (recursive)."""
    types: set[str] = set()

    def walk(obj: dict | list) -> None:
        if isinstance(obj, dict):
            t = obj.get("@type")
            if isinstance(t, str):
                types.add(t)
            elif isinstance(t, list):
                types.update(t)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    for block in json_ld_blocks:
        walk(block)
    return types


def extract_same_as(json_ld_blocks: list[dict]) -> list[str]:
    """Collect all sameAs URLs from JSON-LD."""
    same_as_urls: list[str] = []

    def walk(obj: dict | list) -> None:
        if isinstance(obj, dict):
            sa = obj.get("sameAs")
            if isinstance(sa, str):
                same_as_urls.append(sa)
            elif isinstance(sa, list):
                same_as_urls.extend(s for s in sa if isinstance(s, str))
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    for block in json_ld_blocks:
        walk(block)
    return same_as_urls


def audit_entity_schema(base_url: str) -> dict:
    """Fetch homepage and check entity schemas and sameAs signals."""
    result = {
        "reachable": False,
        "schema_types": [],
        "has_organization": False,
        "has_website": False,
        "has_article": False,
        "has_person": False,
        "has_faq": False,
        "has_howto": False,
        "same_as_urls": [],
        "same_as_authoritative_count": 0,
        "same_as_wikidata": False,
        "same_as_wikipedia": False,
        "same_as_linkedin": False,
    }

    resp = fetch(base_url)
    if resp is None or resp.status_code != 200:
        return result

    result["reachable"] = True
    soup = BeautifulSoup(resp.text, "html.parser")
    json_ld = extract_json_ld(soup)
    types = collect_schema_types(json_ld)
    result["schema_types"] = sorted(types)

    result["has_organization"] = "Organization" in types
    result["has_website"] = "WebSite" in types
    result["has_article"] = bool(types & {"Article", "NewsArticle"})
    result["has_person"] = "Person" in types
    result["has_faq"] = "FAQPage" in types
    result["has_howto"] = "HowTo" in types

    same_as = extract_same_as(json_ld)
    result["same_as_urls"] = same_as

    auth_count = 0
    for url in same_as:
        if "wikidata.org" in url:
            result["same_as_wikidata"] = True
            auth_count += 1
        if "wikipedia.org" in url:
            result["same_as_wikipedia"] = True
            auth_count += 1
        if "linkedin.com/company" in url:
            result["same_as_linkedin"] = True
            auth_count += 1
        for domain in AUTHORITATIVE_SAME_AS_DOMAINS:
            if domain in url:
                auth_count += 1
                break

    result["same_as_authoritative_count"] = auth_count
    return result


# ---------------------------------------------------------------------------
# Page-level schema and content analysis
# ---------------------------------------------------------------------------

def audit_page(url: str) -> dict:
    """Audit a single page for GEO-relevant signals."""
    result = {
        "url": url,
        "status": None,
        "schema_types": [],
        "has_faq_schema": False,
        "has_howto_schema": False,
        "has_article_schema": False,
        "has_author_same_as": False,
        "question_headings": 0,
        "total_headings": 0,
        "word_count": 0,
        "first_paragraph_word_count": 0,
        "title": None,
        "has_meta_description": False,
    }

    resp = fetch(url)
    if resp is None:
        result["status"] = 0
        return result

    result["status"] = resp.status_code
    if resp.status_code != 200:
        return result

    soup = BeautifulSoup(resp.text, "html.parser")

    # Title
    title_tag = soup.find("title")
    result["title"] = title_tag.get_text(strip=True) if title_tag else None

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    result["has_meta_description"] = meta_desc is not None and bool(
        meta_desc.get("content", "").strip()
    )

    # JSON-LD
    json_ld = extract_json_ld(soup)
    types = collect_schema_types(json_ld)
    result["schema_types"] = sorted(types)
    result["has_faq_schema"] = "FAQPage" in types
    result["has_howto_schema"] = "HowTo" in types
    result["has_article_schema"] = bool(types & {"Article", "NewsArticle"})

    # Author sameAs
    same_as = extract_same_as(json_ld)
    result["has_author_same_as"] = any(
        "wikidata.org" in u or "wikipedia.org" in u or "linkedin.com" in u
        for u in same_as
    )

    # Heading analysis
    headings = soup.find_all(["h1", "h2", "h3", "h4"])
    result["total_headings"] = len(headings)
    question_count = sum(
        1 for h in headings if QUESTION_PREFIXES.match(h.get_text(strip=True))
    )
    result["question_headings"] = question_count

    # Word count (body text only, rough estimate)
    body = soup.find("body")
    if body:
        body_text = body.get_text(" ", strip=True)
        result["word_count"] = len(body_text.split())

    # First paragraph word count
    first_p = soup.find("p")
    if first_p:
        result["first_paragraph_word_count"] = len(
            first_p.get_text(strip=True).split()
        )

    return result


def discover_sample_urls(base_url: str, n: int) -> list[str]:
    """Discover up to n internal page URLs from the sitemap or homepage links."""
    urls: list[str] = [base_url]

    # Try sitemap
    sitemap_text = fetch_text(urllib.parse.urljoin(base_url, "/sitemap.xml"))
    if sitemap_text:
        locs = re.findall(r"<loc>(.*?)</loc>", sitemap_text)
        parsed_base = urllib.parse.urlparse(base_url)
        for loc in locs:
            if len(urls) >= n + 1:
                break
            parsed = urllib.parse.urlparse(loc)
            if parsed.netloc == parsed_base.netloc:
                urls.append(loc)

    # Fall back to homepage links if sitemap gave too few
    if len(urls) < n + 1:
        resp = fetch(base_url)
        if resp and resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            parsed_base = urllib.parse.urlparse(base_url)
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full = urllib.parse.urljoin(base_url, href)
                parsed = urllib.parse.urlparse(full)
                if (
                    parsed.netloc == parsed_base.netloc
                    and full not in urls
                    and not any(
                        seg in parsed.path
                        for seg in ["/admin", "/account", "?", "#"]
                    )
                ):
                    urls.append(full)
                if len(urls) >= n + 1:
                    break

    return urls[: n + 1]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_score(
    robots: dict,
    llms: dict,
    entity: dict,
    pages: list[dict],
) -> tuple[int, list[str]]:
    """Compute GEO score 0-100 and list of finding strings."""
    score = 0
    findings: list[str] = []

    # --- robots.txt AI crawler access (20 pts) ---
    declared_crawlers = [c for c in AI_CRAWLERS if robots.get(c, {}).get("declared")]
    blocked_crawlers = [
        c for c in AI_CRAWLERS if robots.get(c, {}).get("blocked")
    ]

    if robots.get("present"):
        score += 5
        findings.append("[x] robots.txt present")
    else:
        findings.append("[ ] robots.txt missing")

    crawlers_ok = [c for c in AI_CRAWLERS if not robots.get(c, {}).get("blocked")]
    score += min(15, len(crawlers_ok) * 2)

    for crawler in AI_CRAWLERS:
        info = robots.get(crawler, {})
        if info.get("blocked"):
            findings.append(f"[ ] {crawler} is BLOCKED in robots.txt")
        elif info.get("declared"):
            findings.append(f"[x] {crawler} explicitly allowed in robots.txt")
        else:
            findings.append(
                f"[ ] {crawler} not explicitly declared (wildcard applies)"
            )

    # --- llms.txt (20 pts) ---
    if llms.get("present"):
        score += 10
        findings.append(f"[x] /llms.txt found ({llms.get('raw_lines', 0)} lines)")
        if llms.get("has_description"):
            score += 2
            findings.append("[x] llms.txt has description")
        else:
            findings.append("[ ] llms.txt missing description")
        if llms.get("has_preferred_citation"):
            score += 4
            findings.append("[x] llms.txt has preferred citation format")
        else:
            findings.append("[ ] llms.txt missing preferred citation format")
        if llms.get("has_content_scope"):
            score += 4
            findings.append("[x] llms.txt has content scope declarations")
        else:
            findings.append("[ ] llms.txt missing content scope declarations")
    else:
        findings.append("[ ] /llms.txt NOT FOUND — highest priority GEO gap")

    # --- entity schema (25 pts) ---
    if entity.get("has_organization"):
        score += 8
        findings.append("[x] Organization schema present on homepage")
    else:
        findings.append("[ ] Organization schema MISSING from homepage")

    if entity.get("has_website"):
        score += 4
        findings.append("[x] WebSite schema present on homepage")
    else:
        findings.append("[ ] WebSite schema missing from homepage")

    same_as_count = entity.get("same_as_authoritative_count", 0)
    if entity.get("same_as_wikidata"):
        score += 5
        findings.append("[x] sameAs: Wikidata entity linked")
    else:
        findings.append("[ ] sameAs: Wikidata NOT linked")

    if entity.get("same_as_wikipedia"):
        score += 4
        findings.append("[x] sameAs: Wikipedia article linked")
    else:
        findings.append("[ ] sameAs: Wikipedia NOT linked")

    if entity.get("same_as_linkedin"):
        score += 2
        findings.append("[x] sameAs: LinkedIn company linked")
    else:
        findings.append("[ ] sameAs: LinkedIn not linked")

    extra_auth = max(0, same_as_count - 3)
    score += min(2, extra_auth)

    # --- content schema on pages (20 pts) ---
    faq_pages = sum(1 for p in pages if p.get("has_faq_schema"))
    howto_pages = sum(1 for p in pages if p.get("has_howto_schema"))
    article_pages = sum(1 for p in pages if p.get("has_article_schema"))

    if faq_pages > 0:
        score += 5
        findings.append(f"[x] FAQPage schema found on {faq_pages}/{len(pages)} sampled pages")
    else:
        findings.append("[ ] FAQPage schema NOT found on any sampled pages")

    if howto_pages > 0:
        score += 4
        findings.append(f"[x] HowTo schema found on {howto_pages}/{len(pages)} sampled pages")
    else:
        findings.append("[ ] HowTo schema NOT found on any sampled pages")

    if article_pages > 0:
        score += 5
        findings.append(f"[x] Article/NewsArticle schema on {article_pages}/{len(pages)} sampled pages")
    else:
        findings.append("[ ] Article schema NOT found on any sampled pages")

    author_same_as_pages = sum(1 for p in pages if p.get("has_author_same_as"))
    if author_same_as_pages > 0:
        score += 6
        findings.append(f"[x] Author sameAs found on {author_same_as_pages}/{len(pages)} sampled pages")
    else:
        findings.append("[ ] Author sameAs NOT found on any sampled pages")

    # --- content structure (15 pts) ---
    total_headings = sum(p.get("total_headings", 0) for p in pages)
    question_headings = sum(p.get("question_headings", 0) for p in pages)

    if total_headings > 0:
        ratio = question_headings / total_headings
        q_score = int(ratio * 8)
        score += q_score
        findings.append(
            f"{'[x]' if ratio >= 0.5 else '[ ]'} Question-format headings: "
            f"{question_headings}/{total_headings} ({ratio:.0%})"
        )
    else:
        findings.append("[ ] No headings found in sampled pages")

    short_first_p = sum(
        1
        for p in pages
        if 0 < p.get("first_paragraph_word_count", 0) <= 80
    )
    if short_first_p > 0:
        score += 4
        findings.append(
            f"[x] Short opening paragraphs (answer-first style): "
            f"{short_first_p}/{len(pages)} sampled pages"
        )
    else:
        findings.append(
            "[ ] Opening paragraphs may bury answers — check for answer-first structure"
        )

    meta_desc_pages = sum(1 for p in pages if p.get("has_meta_description"))
    if meta_desc_pages == len(pages):
        score += 3
        findings.append("[x] Meta descriptions present on all sampled pages")
    elif meta_desc_pages > 0:
        score += 1
        findings.append(
            f"[ ] Meta descriptions missing on {len(pages) - meta_desc_pages}/{len(pages)} pages"
        )
    else:
        findings.append("[ ] Meta descriptions MISSING from all sampled pages")

    return min(100, score), findings


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_markdown_report(
    url: str,
    score: int,
    findings: list[str],
    robots: dict,
    llms: dict,
    entity: dict,
    pages: list[dict],
    cms_hint: str | None,
) -> str:
    """Produce a markdown GEO audit report."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# GEO Audit: {url}",
        f"",
        f"**Audit date:** {now}  ",
        f"**Score: {score}/100**",
        f"",
        "---",
        "",
        "## AI Crawler Access (robots.txt)",
        "",
    ]

    for c in AI_CRAWLERS:
        info = robots.get(c, {})
        if info.get("blocked"):
            lines.append(f"- [ ] {c}: BLOCKED")
        elif info.get("declared"):
            lines.append(f"- [x] {c}: explicitly allowed")
        else:
            lines.append(f"- [ ] {c}: not declared (wildcard applies)")

    lines += ["", "## llms.txt", ""]
    if llms.get("present"):
        lines.append(f"- [x] /llms.txt found")
        lines.append(
            f"  - Description: {'yes' if llms.get('has_description') else 'NO'}"
        )
        lines.append(
            f"  - Preferred citation: "
            f"{'yes' if llms.get('has_preferred_citation') else 'NO'}"
        )
        lines.append(
            f"  - Content scope: "
            f"{'yes' if llms.get('has_content_scope') else 'NO'}"
        )
    else:
        lines.append(f"- [ ] /llms.txt NOT FOUND at {llms.get('url')}")

    lines += ["", "## Entity Schema", ""]
    lines.append(
        f"- {'[x]' if entity.get('has_organization') else '[ ]'} "
        f"Organization schema on homepage"
    )
    lines.append(
        f"- {'[x]' if entity.get('has_website') else '[ ]'} "
        f"WebSite schema on homepage"
    )
    lines.append(
        f"- {'[x]' if entity.get('same_as_wikidata') else '[ ]'} "
        f"sameAs: Wikidata"
    )
    lines.append(
        f"- {'[x]' if entity.get('same_as_wikipedia') else '[ ]'} "
        f"sameAs: Wikipedia"
    )
    lines.append(
        f"- {'[x]' if entity.get('same_as_linkedin') else '[ ]'} "
        f"sameAs: LinkedIn"
    )
    if entity.get("same_as_urls"):
        lines.append(f"- Total sameAs links found: {len(entity['same_as_urls'])}")

    lines += ["", "## Structured Data on Sampled Pages", ""]
    for page in pages:
        status = page.get("status", 0)
        page_url = page.get("url", "")
        schema_types = page.get("schema_types", [])
        lines.append(
            f"- `{page_url}` (HTTP {status}) — schemas: "
            f"{', '.join(schema_types) if schema_types else 'none detected'}"
        )

    lines += ["", "## Content Structure", ""]
    total_h = sum(p.get("total_headings", 0) for p in pages)
    q_h = sum(p.get("question_headings", 0) for p in pages)
    if total_h > 0:
        lines.append(
            f"- Question-format headings: {q_h}/{total_h} "
            f"({q_h/total_h:.0%})"
        )

    lines += ["", "## Full Finding List", ""]
    for finding in findings:
        lines.append(f"- {finding}")

    lines += ["", "## Recommendations (priority order)", ""]
    recommendations = _build_recommendations(score, robots, llms, entity, pages)
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")

    if cms_hint:
        lines += [
            "",
            f"## CMS-Specific Notes ({cms_hint})",
            "",
            f"See the GEO skill SKILL.md for {cms_hint}-specific implementation guidance.",
        ]

    lines.append("")
    return "\n".join(lines)


def _build_recommendations(
    score: int,
    robots: dict,
    llms: dict,
    entity: dict,
    pages: list[dict],
) -> list[str]:
    recs: list[str] = []

    if not llms.get("present"):
        recs.append(
            "Create /llms.txt immediately: add description, preferred citation format, "
            "allowed/disallowed content scopes. Zero-cost; highest-value GEO signal."
        )

    if not entity.get("same_as_wikidata"):
        recs.append(
            "Add Wikidata entity to Organization sameAs. Create or claim the Wikidata "
            "entity for your organization. This is the most important entity anchor for LLMs."
        )

    if not entity.get("same_as_wikipedia"):
        recs.append(
            "Link Organization sameAs to Wikipedia article. Create or cite the Wikipedia "
            "article for your organization if one exists."
        )

    blocked = [c for c in AI_CRAWLERS if robots.get(c, {}).get("blocked")]
    if blocked:
        recs.append(
            f"Un-block AI crawlers in robots.txt: {', '.join(blocked)}. "
            "These crawlers feed citation systems."
        )

    faq_pages = sum(1 for p in pages if p.get("has_faq_schema"))
    if faq_pages == 0:
        recs.append(
            "Add FAQPage JSON-LD to FAQ/help content. Each FAQ is a direct answer "
            "surface for AI systems. Include question-and-answer pairs in JSON-LD."
        )

    if not entity.get("has_organization"):
        recs.append(
            "Add Organization JSON-LD to homepage with name, url, logo, description, "
            "and sameAs links. This establishes your entity identity for LLMs."
        )

    if not llms.get("has_preferred_citation") and llms.get("present"):
        recs.append(
            "Add preferred citation format to /llms.txt so AI systems know how to "
            "attribute content from your site."
        )

    howto_pages = sum(1 for p in pages if p.get("has_howto_schema"))
    if howto_pages == 0:
        recs.append(
            "Add HowTo JSON-LD to procedural/guide content. Step-by-step content "
            "with HowTo markup is highly cited in AI-generated instructions."
        )

    return recs[:8]  # Top 8


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="GEO Audit: audit a web property for AI discoverability signals."
    )
    parser.add_argument("--url", required=True, help="Base URL to audit")
    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Number of additional pages to sample (default: 5)",
    )
    parser.add_argument(
        "--output",
        default="./geo-output",
        help="Output directory (default: ./geo-output)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--cms",
        default=None,
        help="CMS hint for platform-specific guidance",
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    if not base_url.startswith("http"):
        base_url = "https://" + base_url

    print(f"GEO Audit: {base_url}")
    print(f"Sampling {args.pages} additional pages beyond homepage.")

    # 1. robots.txt
    print("  Checking robots.txt...")
    robots = audit_robots(base_url)
    time.sleep(DELAY_BETWEEN_REQUESTS)

    # 2. llms.txt
    print("  Checking llms.txt...")
    llms = audit_llms_txt(base_url)
    time.sleep(DELAY_BETWEEN_REQUESTS)

    # 3. Entity schema on homepage
    print("  Auditing entity schema on homepage...")
    entity = audit_entity_schema(base_url)
    time.sleep(DELAY_BETWEEN_REQUESTS)

    # 4. Sample pages
    print(f"  Discovering sample URLs...")
    sample_urls = discover_sample_urls(base_url, args.pages)
    print(f"  Auditing {len(sample_urls)} page(s)...")
    pages: list[dict] = []
    for page_url in sample_urls:
        print(f"    -> {page_url}")
        page_data = audit_page(page_url)
        pages.append(page_data)
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # 5. Score
    score, findings = compute_score(robots, llms, entity, pages)
    print(f"\nGEO Score: {score}/100")

    # 6. Output
    os.makedirs(args.output, exist_ok=True)

    if args.format in ("markdown", "both"):
        md = generate_markdown_report(
            base_url, score, findings, robots, llms, entity, pages, args.cms
        )
        md_path = os.path.join(args.output, "geo-report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Report written: {md_path}")

    if args.format in ("json", "both"):
        data = {
            "url": base_url,
            "score": score,
            "findings": findings,
            "robots": {k: v for k, v in robots.items() if k != "crawlers"},
            "llms_txt": llms,
            "entity_schema": entity,
            "pages": pages,
        }
        json_path = os.path.join(args.output, "geo-data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Data written: {json_path}")


if __name__ == "__main__":
    main()
