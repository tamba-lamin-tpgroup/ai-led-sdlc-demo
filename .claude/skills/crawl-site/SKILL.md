---
name: crawl-site
description: >
  Crawl any website to generate a content inventory with per-URL SEO metadata,
  HTTP status, headings, images, links, and schema types. Supports local dev
  (DDEV/localhost) and remote targets. Accepts a sitemap URL, sitemap file, or
  auto-discovers. Outputs CSV inventory + JSON link map. Use when asked to crawl,
  inventory, or analyze any website's pages and structure.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
argument-hint: "--url URL [--local] [--sitemap URL|FILE] [--max-pages N] [--output DIR] [--exclude PATTERN] [--screenshots] [--scope PATH]"
---

# Web Crawler Skill

Crawls any web property and generates a structured content inventory.

## Quick Start

```
/crawl-site --url https://example.com
/crawl-site --url https://mysite.ddev.site --local
/crawl-site --url https://example.com --sitemap https://example.com/sitemap.xml --max-pages 5000
/crawl-site --url https://example.com --sitemap /path/to/local-sitemap.xml
/crawl-site --url https://example.com --scope /news --screenshots --output ./news-crawl
```

## All Options

| Option | Default | Description |
|--------|---------|-------------|
| `--url URL` | **required** | Base URL to crawl |
| `--local` | false | Local/dev site: disable SSL verification |
| `--sitemap URL\|FILE` | auto-detect | Sitemap URL or local XML file path |
| `--max-pages N` | 1000 | Maximum pages to crawl (0 = unlimited) |
| `--output DIR` | `./crawl-output` | Output directory |
| `--exclude PATTERN` | none | Regex URL exclusion (repeatable) |
| `--include PATTERN` | none | Only crawl matching URLs (repeatable) |
| `--scope PATH` | none | Restrict to path prefix (e.g. /news) |
| `--concurrency N` | 5 | Parallel request workers |
| `--timeout N` | 15 | Per-request timeout in seconds |
| `--screenshots` | false | Capture full-page PNGs (requires Playwright) |
| `--depth N` | 10 | Max BFS depth from start URL |
| `--delay MS` | 0 | Delay between requests (ms) |
| `--user-agent STR` | SEO-Audit-Bot/1.0 | Custom user agent |
| `--no-sitemap` | false | Skip sitemap discovery, use BFS only |

## Prerequisites

```bash
pip3 install requests beautifulsoup4 lxml tqdm pandas --break-system-packages -q
# For screenshots only:
pip3 install playwright --break-system-packages -q && python3 -m playwright install chromium
```

## Execution

Run the bundled crawler script:

```bash
python3 "$CLAUDE_SKILL_DIR/crawler.py" $ARGUMENTS
```

## Output Files

| File | Description |
|------|-------------|
| `inventory.csv` | Full per-URL metadata (30+ columns) |
| `link-map.json` | Internal link graph `{source: [targets]}` |
| `redirects.csv` | All redirects with full chain |
| `errors.csv` | 4xx and 5xx responses |
| `sitemap-urls.txt` | Raw URL list from sitemap |
| `urls-to-crawl.txt` | Final crawl list after filtering |
| `crawl-log.txt` | Timestamped request log |
| `screenshots/` | Full-page PNGs (if --screenshots) |

## Inventory CSV Columns

`url, http_status, redirect_target, redirect_chain_length, title, title_length,
title_missing, meta_description, meta_description_length, meta_description_missing,
canonical_url, canonical_missing, canonical_is_self, meta_robots, h1_text, h1_count,
h1_missing, h2_count, h3_count, word_count, image_count, images_missing_alt,
internal_link_count, external_link_count, has_og_title, has_og_description,
has_og_image, has_twitter_card, schema_types, response_time_ms, page_size_bytes,
content_type, last_modified_header, screenshot_path`

## After Crawling

Feed the output into other skills:
- `/seo-audit --input ./crawl-output` — run full SEO analysis
- `/tech-stack-audit --url URL` — focused technology fingerprint
- `/audit-pptx --input ./crawl-output` — generate PowerPoint report
