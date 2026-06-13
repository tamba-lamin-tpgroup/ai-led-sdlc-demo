---
name: audit-pptx
description: >
  Generate a professional PowerPoint presentation from SEO and web audit findings.
  Reads CSV and markdown outputs from /seo-audit, /crawl-site, and /tech-stack-audit.
  Always includes a Methodology slide. Fully configurable: client name, company,
  brand color, logo. Slides include: Cover, Agenda, Methodology, Audit Scope,
  SEO Health Dashboard, Critical Issues, On-Page SEO, Technical SEO, GEO/Structured
  Data, Crawl Budget, Recommendations, and Next Steps. Use whenever a PowerPoint
  deliverable is needed from any web audit.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
argument-hint: "--input DIR [--output FILE] [--client NAME] [--company NAME] [--brand-color HEX] [--logo PATH] [--url URL]"
---

# Audit PowerPoint Generator

Generates a professional, branded PowerPoint from SEO/web audit output.

## Quick Start

```
/audit-pptx --input ./seo-audit-output
/audit-pptx --input ./seo-audit-output --client "Acme Corp" --company "My Agency"
/audit-pptx --input ./seo-audit-output --brand-color "#E63946" --logo ./logo.png
/audit-pptx --input ./seo-audit-output --output ~/Desktop/client-seo-audit.pptx
```

## All Options

| Option | Default | Description |
|--------|---------|-------------|
| `--input DIR` | **required** | Directory with audit CSV/report output |
| `--output FILE` | `{input}/seo-audit-report.pptx` | Output PPTX file path |
| `--client NAME` | `Website` | Client / project name (slide headers) |
| `--company NAME` | `SEO Audit` | Auditing company name (slide footers) |
| `--brand-color HEX` | `#1a1a2e` | Primary brand color (headers, accents) |
| `--accent-color HEX` | auto | Accent color (derived from brand if omitted) |
| `--logo PATH` | none | Logo image file for cover and footer |
| `--url URL` | auto | Target URL (read from audit data if omitted) |
| `--date STR` | today | Audit date override (e.g. "May 2026") |
| `--no-geo` | false | Skip GEO slides even if data exists |
| `--confidential` | false | Add confidentiality footer to all slides |

## Prerequisites

```bash
pip3 install python-pptx --break-system-packages -q
```

## Execution

```bash
python3 "$CLAUDE_SKILL_DIR/generate_audit_pptx.py" $ARGUMENTS
```

## Slide Deck Structure

| # | Slide | Data Source |
|---|-------|-------------|
| 1 | **Cover** | Client name, URL, audit date, company logo |
| 2 | **Agenda** | Auto-generated from included sections |
| 3 | **Methodology** | Audit phases, tools used, scope, limitations |
| 4 | **Audit Scope & Summary** | URL counts, HTTP status distribution |
| 5 | **SEO Health Dashboard** | Score card with 7 dimension bars |
| 6 | **Top 10 Critical Issues** | From recommendations.csv |
| 7 | **On-Page SEO Findings** | Titles, meta descriptions, H1 data |
| 8 | **Technical SEO Findings** | Errors, redirects, canonicals |
| 9 | **Image & Alt Text** | Alt text coverage |
| 10 | **GEO / Structured Data** | Schema coverage (if geo data present) |
| 11 | **AI Crawlability** | robots.txt, llms.txt, bot access |
| 12 | **Crawl Budget Analysis** | URL waste metrics |
| 13 | **Findability** | Orphan pages, click depth, breadcrumbs |
| 14 | **Recommendations** | Priority matrix table |
| 15 | **Next Steps** | Quick wins vs strategic actions |
| 16 | **Appendix** | Data table references, methodology notes |

## Methodology Slide Content

The methodology slide is always included and documents:
- **Audit approach:** Tool-based automated crawl (not manual review)
- **Phases executed:** URL Discovery, SEO Crawl, GEO Audit (if run), Analysis
- **Tools used:** Python crawler, extruct, requests, BeautifulSoup
- **Scope:** Total URLs, pages crawled, sample sizes
- **Data collection date:** Automatically populated
- **Limitations:** Local vs live site differences, JS-rendered content caveat,
  WAF behavior on live site, screenshot sampling limits

## Branding

The deck uses `--brand-color` for:
- Slide header bars
- Section divider slides
- Score bar fill
- Critical issue severity chips

Default palette when no brand color is specified:
- Primary: `#1a1a2e` (dark navy)
- Accent: `#e94560` (red)
- Success: `#00b050` (green)
- Warning: `#ffc000` (amber)
- Critical: `#da291c` (red)
- Text: `#2c2c2c` (dark grey)
- Background: `#ffffff` (white)
