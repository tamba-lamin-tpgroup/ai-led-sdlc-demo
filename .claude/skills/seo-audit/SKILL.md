---
name: seo-audit
description: >
  Run a full SEO and GEO (Generative Engine Optimization) audit on any web property.
  Produces per-URL SEO signals, duplicate detection, structured data coverage, AI
  crawlability analysis, crawl budget metrics, findability analysis, and markdown
  reports. Works from an existing crawl inventory or runs its own URL discovery.
  Use when asked to audit SEO, analyze structured data, check GEO readiness, assess
  crawl budget, or generate SEO reports for any website.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
argument-hint: "--url URL [--input DIR] [--local] [--sitemap URL|FILE] [--max-pages N] [--output DIR] [--exclude PATTERN] [--geo] [--client NAME] [--company NAME] [--brand-color HEX] [--cms drupal|wordpress|generic] [--pptx]"
---

# SEO Audit Skill

Runs a comprehensive SEO and GEO audit, generating CSV data and markdown reports.

## Quick Start

```
/seo-audit --url https://example.com
/seo-audit --url https://mysite.ddev.site --local --geo
/seo-audit --input ./crawl-output --client "Acme Corp" --company "My Agency"
/seo-audit --url https://example.com --geo --pptx --client "Client Name"
```

## All Options

| Option | Default | Description |
|--------|---------|-------------|
| `--url URL` | required* | Base URL to audit |
| `--input DIR` | none | Use existing crawl output from `/crawl-site` |
| `--local` | false | Local/dev site: disable SSL verification |
| `--sitemap URL\|FILE` | auto | Sitemap URL or local XML file |
| `--max-pages N` | 1000 | Maximum pages to audit |
| `--output DIR` | `./seo-audit-output` | Output directory |
| `--exclude PATTERN` | none | Regex exclusion (repeatable) |
| `--scope PATH` | none | Restrict to path prefix |
| `--geo` | false | Include GEO / AI crawlability analysis |
| `--client NAME` | `Website` | Client/project name for report headers |
| `--company NAME` | `SEO Audit` | Auditing company name |
| `--brand-color HEX` | `#1a1a2e` | Report accent color |
| `--cms TYPE` | `generic` | CMS hint: drupal, wordpress, generic |
| `--pptx` | false | Generate PowerPoint on completion |

*If `--input` is provided, `--url` is optional (used only for display).

## Prerequisites

```bash
pip3 install requests beautifulsoup4 lxml extruct tqdm pandas --break-system-packages -q
```

## Execution

```bash
python3 "$CLAUDE_SKILL_DIR/seo_audit.py" $ARGUMENTS
```

## What Gets Audited

### SEO Signals (per URL)
- Title tag: presence, length, duplicates
- Meta description: presence, length, duplicates
- Canonical URL: presence, self-reference, conflicts (/node/NNN vs clean path)
- Meta robots and X-Robots-Tag directives
- H1/H2/H3 heading presence and counts
- Word count (body text)
- Image alt text coverage
- Internal and external link counts
- OpenGraph and Twitter Card completeness
- Schema.org types present (JSON-LD)
- HTTP status and redirect chains
- Response time and page size

### GEO Signals (with --geo)
- Schema.org entity coverage: Organization, Person, Article, Event, FAQPage,
  HowTo, BreadcrumbList, JobPosting, SpeakableSpecification
- Entity relationship integrity: @id cross-references
- robots.txt AI bot rules: GPTBot, ClaudeBot, PerplexityBot, CCBot, anthropic-ai
- llms.txt presence and quality
- JavaScript rendering risk
- E-E-A-T signals: author attribution, publication dates, organizational schema
- FAQ schema opportunities (pages with Q&A patterns but no FAQPage schema)
- Content freshness: modification dates from schema and sitemaps

### Crawl Budget Analysis
- URL pattern waste quantification
- robots.txt completeness (admin paths, API endpoints, pagination params)
- Sitemap health (status codes, lastmod, priority)

### Findability Analysis
- Internal link graph (sampled)
- Orphan page detection (0 inbound links)
- Click depth from homepage
- BreadcrumbList schema coverage

## Output Files

```
{output}/
├── csv/
│   ├── seo_crawl_raw.csv           Full per-URL SEO data
│   ├── seo_errors.csv              4xx/5xx responses
│   ├── seo_redirects.csv           Redirect chains
│   ├── seo_duplicate_titles.csv    Duplicate title groups
│   ├── seo_duplicate_meta.csv      Duplicate meta groups
│   ├── seo_images_no_alt.csv       Pages with missing alt text
│   ├── geo_structured_data.csv     Schema.org per URL (with --geo)
│   ├── geo_entity_relationships.csv  Entity coverage by type
│   ├── geo_ai_crawlability.csv     AI bot access signals
│   ├── geo_eeat_signals.csv        E-E-A-T per page
│   ├── geo_faq_opportunities.csv   Pages needing FAQPage schema
│   ├── crawl_budget_analysis.csv   URL waste metrics
│   ├── findability_analysis.csv    Link graph + depth
│   └── recommendations.csv         15 prioritized fixes
└── reports/
    ├── 00_executive_summary.md
    ├── 01_seo_findings.md
    ├── 02_geo_findings.md          (with --geo only)
    └── 03_geo_scorecard.md         (with --geo only)
```

## After Auditing

- `/audit-pptx --input {output}` — generate the PowerPoint deliverable
- Review `recommendations.csv` for the prioritized action plan
