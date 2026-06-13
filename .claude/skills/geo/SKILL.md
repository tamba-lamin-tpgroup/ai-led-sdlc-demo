---
name: geo
description: >
  Generative Engine Optimization (GEO) — audit and improve how AI systems
  (ChatGPT, Claude, Perplexity, Gemini, Copilot) discover, understand, cite,
  and surface a web property in AI-generated responses. Works on any site or
  CMS. Use when asked to audit AI visibility, llms.txt, entity authority,
  structured data for LLMs, AI crawler access, or citation optimization.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch, WebSearch
argument-hint: "--url URL [--output DIR] [--cms SLUG]"
---
# Skill: geo (Generative Engine Optimization)

## What GEO is

Generative Engine Optimization (GEO) is the practice of optimizing web
content so that AI systems — including ChatGPT, Claude, Perplexity, Gemini,
Microsoft Copilot, and other LLM-powered answer engines — can discover,
accurately understand, and cite a web property in AI-generated responses.

GEO is distinct from traditional SEO:

- SEO = ranking in blue-link search result pages (SERPs).
- GEO = being discovered, understood, and cited as a trusted source in
  AI-generated answer text, citations, or knowledge summaries.

An LLM that produces an answer about a topic does not show a ranked list of
ten links. It may include zero, one, or several inline citations. GEO
determines whether your site is among those citations or is invisible.

GEO is not a replacement for SEO. Strong SEO signals (authority, crawlability,
structured data) feed GEO. GEO adds AI-specific signals on top.

## llms.txt: the emerging standard

`llms.txt` is a plain-text file placed at the root of a domain
(`https://example.com/llms.txt`) that communicates with AI crawlers in
plain English. The standard is defined at https://llmstxt.org.

### Format

```
# Site: Example Corp
# Description: Enterprise software solutions for manufacturing.
# Preferred citation: "Example Corp documentation" (https://example.com/docs)
# AI crawlers: allowed
# Content scope: /docs/, /blog/, /products/

## Allow list
/docs/
/blog/
/products/

## Disallow list
/account/
/admin/
/internal/

## Contact
AI-queries: ai@example.com
```

### What to include

- Site name and one-sentence description.
- Preferred citation format for AI systems to use.
- Explicit AI crawler stance (allowed / restricted / by-request).
- Content scopes permitted for AI ingestion.
- Disallowed paths (account, admin, staging, PII-containing areas).
- Optional: contact for AI partnership inquiries.
- Optional: preferred language(s) and content type declarations.

### Generation

For CMS-driven sites, generate `llms.txt` dynamically from the sitemap:
extract top-level section paths, verify they are publicly accessible, and
write the file as part of the CI/CD pipeline or as a CMS webhook-triggered
task. Regenerate whenever major content sections change.

## AI crawler access (robots.txt)

AI crawlers respect `robots.txt` like any other crawler. Common AI crawler
user-agent strings and their owners:

| User-agent | System | Notes |
|---|---|---|
| GPTBot | OpenAI (ChatGPT) | Major citation source; blocking reduces ChatGPT visibility |
| ClaudeBot | Anthropic (Claude) | Blocks Claude knowledge retrieval |
| PerplexityBot | Perplexity AI | Blocks Perplexity citations |
| GoogleBot-Extended | Google Gemini | Separate from GoogleBot; controls Gemini access |
| Bingbot (AI mode) | Microsoft Copilot | Same bot as Bing; AI Mode inherits access |
| Diffbot | Diffbot knowledge graph | Used by many enterprise AI systems |
| CCBot | Common Crawl | Foundation for many open-source LLMs |
| OAI-SearchBot | OpenAI Search | Used for real-time web search in ChatGPT |

### Common mistakes

1. Blocking AI crawlers that provide citation traffic (GPTBot especially).
2. No robots.txt entry for GPTBot — means the default allow applies, which
   is correct, but explicit entries signal intentionality.
3. Using `User-agent: *` Disallow rules that accidentally block AI crawlers.
4. Blocking CCBot without understanding that it seeds open-source LLMs.

### Recommended robots.txt additions

```
# Generative Engine Optimization
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: GoogleBot-Extended
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Diffbot
Allow: /

# Block AI crawlers from sensitive areas explicitly
User-agent: GPTBot
Disallow: /account/
Disallow: /admin/
Disallow: /internal/
```

## Entity authority (E-E-A-T for AI)

LLMs assess authority using the same signals as Google's E-E-A-T
(Experience, Expertise, Authoritativeness, Trustworthiness) but weight
structured entity signals more heavily than human editorial signals.

### Schema.org entity markup

The most impactful GEO action is ensuring your site has well-structured
JSON-LD for:

- `Organization` — name, URL, logo, description, founding year, sameAs.
- `WebSite` — name, URL, potentialAction (SearchAction).
- `Person` — for author pages: name, jobTitle, url, sameAs, affiliation.
- `Article` / `NewsArticle` — datePublished, dateModified, author,
  publisher, headline.
- `WebPage` — name, description, url, isPartOf, primaryImageOfPage.

### sameAs links: anchoring your entity

`sameAs` is the single most important GEO signal for entity disambiguation.
An `Organization` with `sameAs` pointing to:

- Wikipedia article
- Wikidata entity (`https://www.wikidata.org/wiki/Q...`)
- LinkedIn company page
- Crunchbase profile
- GLEIF LEI (financial entities)

...tells LLMs that your on-page entity matches these authoritative knowledge
graph nodes. This dramatically improves citation accuracy.

### Example Organization with sameAs

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Example Corp",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "description": "Enterprise software for manufacturing.",
  "foundingDate": "2010",
  "sameAs": [
    "https://en.wikipedia.org/wiki/Example_Corp",
    "https://www.wikidata.org/wiki/Q12345678",
    "https://www.linkedin.com/company/example-corp",
    "https://www.crunchbase.com/organization/example-corp"
  ]
}
```

## Content structure for AI

AI systems prefer content that provides direct, factual answers near the
top of a section. Optimize for:

1. **Direct answers first**: place the answer in the first sentence of a
   section, not at the end. AI summarizers extract opening sentences.
2. **Factual density**: include specific numbers, dates, names, and
   verifiable claims. Vague prose is under-cited.
3. **Clear entity mentions**: name entities explicitly in each section
   rather than relying on pronouns or implied references. "Dell's XPS 15
   laptop" not "the device".
4. **Question-answer heading pairs**: structure content so that H2/H3
   headings read as questions and the first paragraph answers them.
5. **Short paragraphs**: 2-4 sentences per paragraph. AI summarizers
   prefer short, self-contained paragraphs.
6. **Avoid ambiguous references**: "the company" is ambiguous; "Example
   Corp" is not.
7. **Citations and sources**: citing primary sources within your content
   signals to AI that your content is evidence-based.

## Structured data for LLMs

Priority JSON-LD schemas for GEO, in order of impact:

| Schema type | GEO impact | Notes |
|---|---|---|
| Organization + sameAs | Very high | Entity disambiguation |
| Article / NewsArticle | High | Content currency and authorship |
| FAQPage | High | Direct answer surface for AI |
| HowTo | High | Step-by-step content for AI summarization |
| WebSite + SearchAction | Medium | Site-level authority |
| Person (author) | Medium | Author E-E-A-T signals |
| Product | Medium | Product knowledge panels |
| Review / AggregateRating | Medium | Trust signals |
| Event | Low-medium | Temporal authority |
| BreadcrumbList | Low | Navigation context |

### FAQPage example

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is Example Corp's return policy?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Example Corp offers a 30-day return policy for all products purchased directly from example.com. Items must be in original packaging."
      }
    }
  ]
}
```

## Citation audit

Checking whether your site is cited in AI responses is an active
monitoring discipline.

### Manual prompting strategies

Test citation coverage by prompting AI systems with:

- "[Topic] [your brand]" — e.g., "Dell laptop enterprise support options"
- Factual questions your site should answer definitively
- Comparison queries where your product/service is a candidate
- Questions where your unique research or data should appear

Run these prompts across ChatGPT, Claude, Perplexity, and Gemini weekly.
Record which responses cite your domain.

### Monitoring signals

Indirect signals that AI crawlers are active on your site:

- `GPTBot` entries in server access logs
- `ClaudeBot` entries in server access logs
- Referrer traffic from `perplexity.ai`, `chat.openai.com`, `bard.google.com`
- Direct mentions of your domain in AI responses (track via brand monitoring)

### Tools

- Semrush AI Toolkit (citation tracking feature, 2024+)
- Perplexity.ai "sources" panel — check which sources a query cites
- Brand24, Mention — monitor AI-generated brand mentions
- Custom log analysis on access logs for AI bot user-agents

## CMS-specific GEO guidance

### Contentstack

Implement JSON-LD via a Global Field (`seo_metadata`) on all content types.
Use a JSON field for the raw JSON-LD object or build structured fields
(schema_type, schema_data) and serialize on the frontend. Inject in the
Next.js `<head>` via `<Script type="application/ld+json">` in the layout.
Use a webhook to regenerate `llms.txt` when the sitemap changes.

### Contentful

Add a `seoStructuredData` JSON field to all content types. Render JSON-LD in
the Next.js layout. Use the Contentful CLI or Content Management API to
bulk-populate structured data fields. Generate `llms.txt` via a CI script
that reads the Contentful sitemap entries.

### Drupal / Acquia

Use the `schema_metatag` contributed module for automatic JSON-LD generation
from Drupal metadata fields. Enable Organization and WebSite schemas in the
module config. The `xmlsitemap` module feeds `llms.txt` generation. Custom
`llms.txt` route via a simple Drupal controller.

### WordPress

Use Yoast SEO or RankMath to generate structured data. Add custom JSON-LD
via `wp_head` action for Organization and WebSite schemas. Generate
`llms.txt` via a simple plugin that reads the sitemap and writes the file on
save events.

### Sitecore

Use the SXA Metadata component or a custom Razor rendering to inject JSON-LD
in `<head>`. Organization and WebSite schemas are best placed in the shared
layout rendering. Generate `llms.txt` via a custom Sitecore pipeline processor
that writes the file to the web root on publish events.

## GEO checklist (audit output format)

When running a GEO audit, produce a markdown checklist with scores:

```markdown
# GEO Audit: example.com

**Score: 68/100**

## AI Crawler Access
- [x] GPTBot allowed in robots.txt
- [x] ClaudeBot allowed in robots.txt
- [ ] PerplexityBot not explicitly allowed (defaulting to wildcard)
- [ ] GoogleBot-Extended not declared

## llms.txt
- [ ] /llms.txt not found (404)

## Entity Authority
- [x] Organization schema present on homepage
- [x] sameAs: LinkedIn linked
- [ ] sameAs: Wikidata NOT linked
- [ ] sameAs: Wikipedia NOT linked

## Article / Content Schema
- [x] Article schema on blog posts (12/20 sampled pages)
- [ ] 8 blog posts missing datePublished
- [ ] author.sameAs missing on all author profiles

## Structured Data Coverage
- [x] WebSite schema on homepage
- [ ] FAQPage schema missing (site has 15 FAQ pages)
- [ ] HowTo schema missing (site has 8 how-to guides)

## Content Structure
- [x] Most H2s are in question format (14/18 checked)
- [ ] Opening paragraphs often bury the answer (6/18 checked)
- [ ] Pronoun overuse detected: 23 instances of "the company" without
      prior explicit entity mention

## Recommendations (priority order)
1. Add /llms.txt immediately — zero cost, high signal
2. Add Wikidata and Wikipedia sameAs to Organization schema
3. Add FAQPage JSON-LD to all FAQ pages
4. Declare PerplexityBot and GoogleBot-Extended in robots.txt
5. Fix missing datePublished on 8 blog posts
6. Rewrite opening paragraphs to lead with the direct answer
```

## Execution

```bash
python3 "$CLAUDE_SKILL_DIR/geo_audit.py" $ARGUMENTS
```

### Argument interface

```
Required:
  --url URL           Base URL to audit (e.g. https://example.com)

Optional:
  --pages N           Number of pages to sample beyond homepage (default: 5)
  --output DIR        Output directory for report files (default: ./geo-output)
  --format FORMAT     Output format: markdown | json | both (default: markdown)
  --cms SLUG          CMS hint for platform-specific guidance
                      (contentstack | contentful | drupal | wordpress | sitecore)
```

The script produces:
- `geo-report.md` — human-readable checklist with score and recommendations
- `geo-data.json` (if --format json or both) — structured audit data
- Exit code 0 = audit complete, exit code 1 = fatal error
