"""
aeo_audit.py - Answer Engine Optimization (AEO) audit script.

Audits a web property for featured snippet eligibility, People Also Ask (PAA)
coverage potential, FAQPage/HowTo/speakable JSON-LD schema, question-heading
patterns, answer-zone paragraph detection, and list/table snippet candidates.
Produces an AEO score (0-100) and a markdown checklist report.

Dependencies: pip install requests beautifulsoup4
No other dependencies required.

Usage:
    python3 aeo_audit.py --url https://example.com [--pages 5]
        [--output ./aeo-output] [--format markdown|json|both]
        [--keywords keywords.txt]
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

QUESTION_PREFIXES = re.compile(
    r"^(who|what|when|where|why|how|is|are|can|does|do|will|was|were|has|have|should|would|could|may|might)\b",
    re.IGNORECASE,
)

SNIPPET_WORD_MIN = 30
SNIPPET_WORD_MAX = 70
SNIPPET_IDEAL_MIN = 40
SNIPPET_IDEAL_MAX = 60

LIST_SNIPPET_MIN_ITEMS = 4
LIST_SNIPPET_MAX_ITEMS = 12

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; AEOAuditBot/1.0; +https://github.com/anthropic)"
    )
}

REQUEST_TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 0.5


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def fetch(url: str, timeout: int = REQUEST_TIMEOUT) -> "requests.Response | None":
    """Fetch a URL; return Response or None on error."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return resp
    except requests.RequestException as exc:
        print(f"  WARN: fetch failed for {url}: {exc}", file=sys.stderr)
        return None


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

    def walk(obj: "dict | list") -> None:
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


def count_faq_questions(json_ld_blocks: list[dict]) -> int:
    """Count Question entities inside FAQPage blocks."""
    count = 0

    def walk(obj: "dict | list") -> None:
        nonlocal count
        if isinstance(obj, dict):
            if obj.get("@type") == "Question":
                count += 1
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    for block in json_ld_blocks:
        walk(block)
    return count


def count_howto_steps(json_ld_blocks: list[dict]) -> int:
    """Count HowToStep entities inside HowTo blocks."""
    count = 0

    def walk(obj: "dict | list") -> None:
        nonlocal count
        if isinstance(obj, dict):
            if obj.get("@type") in ("HowToStep", "HowToSection"):
                count += 1
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    for block in json_ld_blocks:
        walk(block)
    return count


# ---------------------------------------------------------------------------
# Page-level analysis
# ---------------------------------------------------------------------------

def analyze_headings(soup: BeautifulSoup) -> dict:
    """Analyze heading structure for question-format headings."""
    headings = soup.find_all(["h1", "h2", "h3", "h4"])
    total = len(headings)
    question_headings: list[str] = []
    for h in headings:
        text = h.get_text(strip=True)
        if QUESTION_PREFIXES.match(text):
            question_headings.append(text)

    return {
        "total": total,
        "question_count": len(question_headings),
        "question_texts": question_headings[:10],  # sample
    }


def analyze_snippet_paragraphs(soup: BeautifulSoup) -> dict:
    """Find paragraphs in the snippet word-count zone following question headings."""
    snippet_candidates: list[dict] = []
    all_paragraph_lengths: list[int] = []

    headings = soup.find_all(["h2", "h3"])
    for heading in headings:
        heading_text = heading.get_text(strip=True)
        if not QUESTION_PREFIXES.match(heading_text):
            continue
        # Find the next sibling paragraph
        sibling = heading.find_next_sibling()
        while sibling:
            if sibling.name == "p":
                words = len(sibling.get_text(strip=True).split())
                snippet_candidates.append(
                    {
                        "heading": heading_text[:80],
                        "word_count": words,
                        "in_ideal_zone": SNIPPET_IDEAL_MIN <= words <= SNIPPET_IDEAL_MAX,
                        "in_zone": SNIPPET_WORD_MIN <= words <= SNIPPET_WORD_MAX,
                    }
                )
                break
            elif sibling.name in ("h1", "h2", "h3", "h4"):
                break
            sibling = sibling.find_next_sibling()

    # All paragraph lengths
    for p in soup.find_all("p"):
        words = len(p.get_text(strip=True).split())
        if words > 0:
            all_paragraph_lengths.append(words)

    first_p = soup.find("p")
    first_p_words = len(first_p.get_text(strip=True).split()) if first_p else 0

    return {
        "snippet_candidates": snippet_candidates,
        "ideal_zone_count": sum(1 for c in snippet_candidates if c["in_ideal_zone"]),
        "zone_count": sum(1 for c in snippet_candidates if c["in_zone"]),
        "first_paragraph_words": first_p_words,
        "avg_paragraph_words": (
            int(sum(all_paragraph_lengths) / len(all_paragraph_lengths))
            if all_paragraph_lengths
            else 0
        ),
    }


def analyze_list_snippets(soup: BeautifulSoup) -> dict:
    """Identify ordered and unordered lists that are snippet candidates."""
    list_candidates: list[dict] = []

    for list_tag in soup.find_all(["ul", "ol"]):
        items = list_tag.find_all("li", recursive=False)
        item_count = len(items)
        if item_count < LIST_SNIPPET_MIN_ITEMS:
            continue

        # Check preceding heading
        prev = list_tag.find_previous(["h1", "h2", "h3", "h4"])
        preceding_heading = prev.get_text(strip=True) if prev else None

        # Average item word count
        avg_item_words = (
            sum(len(li.get_text(strip=True).split()) for li in items) / item_count
            if item_count
            else 0
        )

        is_ordered = list_tag.name == "ol"
        list_candidates.append(
            {
                "type": "ordered" if is_ordered else "unordered",
                "item_count": item_count,
                "avg_item_words": round(avg_item_words, 1),
                "preceding_heading": preceding_heading[:80] if preceding_heading else None,
                "eligible": (
                    LIST_SNIPPET_MIN_ITEMS <= item_count <= LIST_SNIPPET_MAX_ITEMS
                    and avg_item_words <= 12
                ),
            }
        )

    return {
        "candidates": list_candidates,
        "eligible_count": sum(1 for c in list_candidates if c.get("eligible")),
    }


def analyze_table_snippets(soup: BeautifulSoup) -> dict:
    """Identify tables that are snippet candidates."""
    table_candidates: list[dict] = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        row_count = len(rows)
        if row_count < 2:
            continue

        # Check for header row
        has_header = bool(table.find("th"))

        # Column count from first row
        first_row = rows[0]
        col_count = len(first_row.find_all(["td", "th"]))

        # Preceding heading
        prev = table.find_previous(["h1", "h2", "h3", "h4"])
        preceding_heading = prev.get_text(strip=True) if prev else None

        table_candidates.append(
            {
                "row_count": row_count,
                "col_count": col_count,
                "has_header": has_header,
                "preceding_heading": preceding_heading[:80] if preceding_heading else None,
                "eligible": (
                    2 <= row_count <= 15 and 2 <= col_count <= 5 and has_header
                ),
            }
        )

    return {
        "candidates": table_candidates,
        "eligible_count": sum(1 for c in table_candidates if c.get("eligible")),
    }


def audit_page(url: str) -> dict:
    """Comprehensive AEO audit of a single page."""
    result = {
        "url": url,
        "status": None,
        "title": None,
        "title_length": 0,
        "meta_description": None,
        "meta_description_length": 0,
        "has_meta_description": False,
        "schema_types": [],
        "has_faq_schema": False,
        "has_howto_schema": False,
        "has_qna_schema": False,
        "has_speakable": False,
        "faq_question_count": 0,
        "howto_step_count": 0,
        "headings": {},
        "snippets": {},
        "lists": {},
        "tables": {},
        "word_count": 0,
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
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    result["title"] = title_text
    result["title_length"] = len(title_text)

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": re.compile("description", re.I)})
    if meta_desc:
        desc_content = meta_desc.get("content", "").strip()
        result["meta_description"] = desc_content
        result["meta_description_length"] = len(desc_content)
        result["has_meta_description"] = bool(desc_content)

    # JSON-LD
    json_ld = extract_json_ld(soup)
    types = collect_schema_types(json_ld)
    result["schema_types"] = sorted(types)
    result["has_faq_schema"] = "FAQPage" in types
    result["has_howto_schema"] = "HowTo" in types
    result["has_qna_schema"] = "QAPage" in types
    result["has_speakable"] = "SpeakableSpecification" in types

    if result["has_faq_schema"]:
        result["faq_question_count"] = count_faq_questions(json_ld)
    if result["has_howto_schema"]:
        result["howto_step_count"] = count_howto_steps(json_ld)

    # Word count (body text rough estimate)
    body = soup.find("body")
    if body:
        result["word_count"] = len(body.get_text(" ", strip=True).split())

    # Heading analysis
    result["headings"] = analyze_headings(soup)

    # Snippet paragraph analysis
    result["snippets"] = analyze_snippet_paragraphs(soup)

    # List snippet analysis
    result["lists"] = analyze_list_snippets(soup)

    # Table snippet analysis
    result["tables"] = analyze_table_snippets(soup)

    return result


def discover_sample_urls(base_url: str, n: int) -> list[str]:
    """Discover up to n internal page URLs from the sitemap or homepage links."""
    urls: list[str] = [base_url]

    # Try sitemap
    try:
        sitemap_url = urllib.parse.urljoin(base_url, "/sitemap.xml")
        sitemap_resp = fetch(sitemap_url)
        if sitemap_resp and sitemap_resp.status_code == 200:
            locs = re.findall(r"<loc>(.*?)</loc>", sitemap_resp.text)
            parsed_base = urllib.parse.urlparse(base_url)
            for loc in locs:
                if len(urls) >= n + 1:
                    break
                parsed = urllib.parse.urlparse(loc)
                if parsed.netloc == parsed_base.netloc and loc not in urls:
                    urls.append(loc)
    except Exception:
        pass

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
                        for seg in ["/admin", "/account", "?", "#", ".pdf"]
                    )
                ):
                    urls.append(full)
                if len(urls) >= n + 1:
                    break

    return urls[: n + 1]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_score(pages: list[dict]) -> tuple[int, list[str]]:
    """Compute AEO score 0-100 and list of findings."""
    score = 0
    findings: list[str] = []
    n = len(pages)
    if n == 0:
        return 0, ["No pages audited"]

    # --- Schema coverage (35 pts) ---
    faq_pages = sum(1 for p in pages if p.get("has_faq_schema"))
    howto_pages = sum(1 for p in pages if p.get("has_howto_schema"))
    qna_pages = sum(1 for p in pages if p.get("has_qna_schema"))
    speakable_pages = sum(1 for p in pages if p.get("has_speakable"))

    if faq_pages > 0:
        score += 15
        findings.append(
            f"[x] FAQPage schema found on {faq_pages}/{n} sampled pages"
        )
    else:
        findings.append("[ ] FAQPage schema NOT found on any sampled pages")

    if howto_pages > 0:
        score += 12
        findings.append(
            f"[x] HowTo schema found on {howto_pages}/{n} sampled pages"
        )
    else:
        findings.append("[ ] HowTo schema NOT found on any sampled pages")

    if qna_pages > 0:
        score += 5
        findings.append(
            f"[x] QAPage schema found on {qna_pages}/{n} sampled pages"
        )
    else:
        findings.append("[ ] QAPage schema not found")

    if speakable_pages > 0:
        score += 3
        findings.append(
            f"[x] Speakable schema found on {speakable_pages}/{n} sampled pages"
        )
    else:
        findings.append("[ ] Speakable schema NOT found")

    # --- Heading structure (20 pts) ---
    total_headings = sum(p.get("headings", {}).get("total", 0) for p in pages)
    question_headings = sum(
        p.get("headings", {}).get("question_count", 0) for p in pages
    )

    if total_headings > 0:
        ratio = question_headings / total_headings
        h_score = int(ratio * 20)
        score += h_score
        findings.append(
            f"{'[x]' if ratio >= 0.5 else '[ ]'} Question-format headings: "
            f"{question_headings}/{total_headings} ({ratio:.0%})"
        )
    else:
        findings.append("[ ] No headings found in sampled pages")

    # --- Answer paragraph zone (20 pts) ---
    ideal_zone_total = sum(
        p.get("snippets", {}).get("ideal_zone_count", 0) for p in pages
    )
    snippet_candidates_total = sum(
        len(p.get("snippets", {}).get("snippet_candidates", [])) for p in pages
    )

    if snippet_candidates_total > 0:
        zone_ratio = ideal_zone_total / snippet_candidates_total
        zone_score = int(zone_ratio * 20)
        score += zone_score
        findings.append(
            f"{'[x]' if zone_ratio >= 0.5 else '[ ]'} Answer paragraphs in snippet zone "
            f"(40-60 words): {ideal_zone_total}/{snippet_candidates_total} question-heading "
            f"sections ({zone_ratio:.0%})"
        )
    else:
        findings.append(
            "[ ] No question-heading + paragraph pairs found for snippet analysis"
        )

    # Average first paragraph length
    avg_first_p = (
        sum(p.get("snippets", {}).get("first_paragraph_words", 0) for p in pages) / n
    )
    if 30 <= avg_first_p <= 80:
        findings.append(
            f"[x] Average first-paragraph length: {avg_first_p:.0f} words "
            f"(answer-first zone)"
        )
    else:
        findings.append(
            f"[ ] Average first-paragraph length: {avg_first_p:.0f} words "
            f"(target 40-60 for answer-first)"
        )

    # --- List snippet candidates (15 pts) ---
    eligible_lists = sum(
        p.get("lists", {}).get("eligible_count", 0) for p in pages
    )
    if eligible_lists > 0:
        score += 10
        findings.append(
            f"[x] {eligible_lists} eligible list snippet candidate(s) found"
        )
    else:
        findings.append("[ ] No eligible list snippet candidates found")

    eligible_tables = sum(
        p.get("tables", {}).get("eligible_count", 0) for p in pages
    )
    if eligible_tables > 0:
        score += 5
        findings.append(
            f"[x] {eligible_tables} eligible table snippet candidate(s) found"
        )
    else:
        findings.append("[ ] No eligible table snippet candidates found")

    # --- Meta tags (10 pts) ---
    meta_desc_pages = sum(1 for p in pages if p.get("has_meta_description"))
    meta_ratio = meta_desc_pages / n

    if meta_ratio == 1.0:
        score += 6
        findings.append("[x] Meta descriptions present on all sampled pages")
    elif meta_ratio > 0.5:
        score += 3
        findings.append(
            f"[ ] Meta descriptions missing on {n - meta_desc_pages}/{n} pages"
        )
    else:
        findings.append("[ ] Meta descriptions missing from majority of sampled pages")

    long_titles = sum(
        1 for p in pages if p.get("title_length", 0) > 60
    )
    if long_titles == 0:
        score += 4
        findings.append("[x] Title tags within 60-character limit on all sampled pages")
    else:
        findings.append(
            f"[ ] {long_titles}/{n} title tags exceed 60 characters"
        )

    return min(100, score), findings


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_markdown_report(
    url: str,
    score: int,
    findings: list[str],
    pages: list[dict],
) -> str:
    """Produce a markdown AEO audit report."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# AEO Audit: {url}",
        f"",
        f"**Audit date:** {now}  ",
        f"**Score: {score}/100**",
        f"",
        "---",
        "",
        "## Schema Coverage",
        "",
    ]

    for page in pages:
        status = page.get("status", 0)
        page_url = page.get("url", "")
        schema_types = page.get("schema_types", [])
        faq_q = page.get("faq_question_count", 0)
        howto_s = page.get("howto_step_count", 0)
        label_parts = []
        if schema_types:
            label_parts.append(f"schemas: {', '.join(schema_types)}")
        if faq_q:
            label_parts.append(f"{faq_q} FAQ questions")
        if howto_s:
            label_parts.append(f"{howto_s} HowTo steps")
        label = "; ".join(label_parts) if label_parts else "no AEO schema detected"
        lines.append(f"- `{page_url}` (HTTP {status}) — {label}")

    lines += ["", "## Heading Analysis", ""]
    for page in pages:
        h = page.get("headings", {})
        total = h.get("total", 0)
        q_count = h.get("question_count", 0)
        if total:
            lines.append(
                f"- `{page.get('url', '')}`: {q_count}/{total} question headings"
            )

    lines += ["", "## Snippet Zone Analysis", ""]
    for page in pages:
        s = page.get("snippets", {})
        candidates = s.get("snippet_candidates", [])
        ideal = s.get("ideal_zone_count", 0)
        if candidates:
            lines.append(
                f"- `{page.get('url', '')}`: {ideal}/{len(candidates)} "
                f"question-answer pairs in snippet zone (40-60 words)"
            )

    lines += ["", "## List and Table Snippet Candidates", ""]
    for page in pages:
        list_count = page.get("lists", {}).get("eligible_count", 0)
        table_count = page.get("tables", {}).get("eligible_count", 0)
        if list_count or table_count:
            lines.append(
                f"- `{page.get('url', '')}`: "
                f"{list_count} eligible list(s), {table_count} eligible table(s)"
            )

    lines += ["", "## Full Finding List", ""]
    for finding in findings:
        lines.append(f"- {finding}")

    lines += ["", "## Recommendations (priority order)", ""]
    recs = _build_recommendations(score, pages)
    for i, rec in enumerate(recs, 1):
        lines.append(f"{i}. {rec}")

    lines.append("")
    return "\n".join(lines)


def _build_recommendations(score: int, pages: list[dict]) -> list[str]:
    recs: list[str] = []
    n = len(pages)
    if n == 0:
        return recs

    faq_pages = sum(1 for p in pages if p.get("has_faq_schema"))
    howto_pages = sum(1 for p in pages if p.get("has_howto_schema"))
    total_headings = sum(p.get("headings", {}).get("total", 0) for p in pages)
    question_headings = sum(p.get("headings", {}).get("question_count", 0) for p in pages)
    ideal_zone = sum(p.get("snippets", {}).get("ideal_zone_count", 0) for p in pages)
    snippet_candidates = sum(
        len(p.get("snippets", {}).get("snippet_candidates", [])) for p in pages
    )

    if faq_pages == 0:
        recs.append(
            "Add FAQPage JSON-LD to FAQ and help content. Each FAQ question answered "
            "in 40-60 words directly targets PAA boxes and paragraph featured snippets."
        )
    elif faq_pages < n // 2:
        recs.append(
            f"Expand FAQPage schema coverage: only {faq_pages}/{n} sampled pages have it. "
            "Add to all FAQ, definition, and Q&A pages."
        )

    if snippet_candidates > 0 and ideal_zone < snippet_candidates // 2:
        recs.append(
            "Shorten answer paragraphs under question headings to 40-60 words. "
            "This is the snippet zone Google extracts paragraph snippets from. "
            "Move supporting detail to a second paragraph below the answer."
        )

    if total_headings > 0 and question_headings < total_headings // 2:
        recs.append(
            "Rewrite H2/H3 headings as questions. Question-format headings are the "
            "primary trigger for featured snippet extraction. At least 50% of headings "
            "should start with Who/What/When/Where/Why/How/Is/Are/Can/Does."
        )

    if howto_pages == 0:
        recs.append(
            "Add HowTo JSON-LD to procedural/guide content. Step-by-step content "
            "with HowTo markup is the primary structured data type for ordered list "
            "snippets and AI Overview inclusion for instructional queries."
        )

    eligible_lists = sum(p.get("lists", {}).get("eligible_count", 0) for p in pages)
    if eligible_lists == 0:
        recs.append(
            "Create list-format content for 'best', 'top', 'steps', and 'ways' queries. "
            "Ordered and unordered lists with 5-8 items are the second most common "
            "featured snippet type after paragraph snippets."
        )

    speakable_pages = sum(1 for p in pages if p.get("has_speakable"))
    if speakable_pages == 0 and faq_pages > 0:
        recs.append(
            "Add Speakable JSON-LD (SpeakableSpecification) to FAQ and article pages. "
            "Mark the section and/or article headline CSS selectors. Improves voice "
            "search result eligibility for Google Assistant."
        )

    meta_ok = sum(
        1 for p in pages
        if p.get("has_meta_description") and 100 <= p.get("meta_description_length", 0) <= 160
    )
    if meta_ok < n:
        recs.append(
            f"Optimize meta descriptions: target 100-160 characters, phrased as a "
            f"direct answer or value proposition. Currently {meta_ok}/{n} sampled pages "
            f"have well-formed meta descriptions."
        )

    return recs[:8]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AEO Audit: audit a web property for answer engine optimization signals."
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
        default="./aeo-output",
        help="Output directory (default: ./aeo-output)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--keywords",
        default=None,
        help="Path to keywords file (one keyword/query per line)",
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    if not base_url.startswith("http"):
        base_url = "https://" + base_url

    print(f"AEO Audit: {base_url}")
    print(f"Sampling {args.pages} additional pages beyond homepage.")

    if args.keywords:
        try:
            with open(args.keywords, "r", encoding="utf-8") as f:
                keywords = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(keywords)} keywords from {args.keywords}")
        except OSError as exc:
            print(f"WARN: could not read keywords file: {exc}", file=sys.stderr)

    # Discover sample URLs
    print("  Discovering sample URLs...")
    sample_urls = discover_sample_urls(base_url, args.pages)
    print(f"  Auditing {len(sample_urls)} page(s)...")

    pages: list[dict] = []
    for page_url in sample_urls:
        print(f"    -> {page_url}")
        page_data = audit_page(page_url)
        pages.append(page_data)
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # Score
    score, findings = compute_score(pages)
    print(f"\nAEO Score: {score}/100")

    # Output
    os.makedirs(args.output, exist_ok=True)

    if args.format in ("markdown", "both"):
        md = generate_markdown_report(base_url, score, findings, pages)
        md_path = os.path.join(args.output, "aeo-report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Report written: {md_path}")

    if args.format in ("json", "both"):
        data = {
            "url": base_url,
            "score": score,
            "findings": findings,
            "pages": pages,
        }
        json_path = os.path.join(args.output, "aeo-data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Data written: {json_path}")


if __name__ == "__main__":
    main()
