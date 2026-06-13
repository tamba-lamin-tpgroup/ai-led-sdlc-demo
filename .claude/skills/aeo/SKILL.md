---
name: aeo
description: >
  Answer Engine Optimization (AEO) — audit and improve how a web property
  appears in answer engines: featured snippets (Position Zero), People Also
  Ask (PAA), Knowledge Panels, voice search results, and AI-powered SERP
  features. Use when asked to audit snippet eligibility, PAA coverage,
  FAQ schema, voice search readiness, or direct-answer optimization.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch, WebSearch
argument-hint: "--url URL [--output DIR] [--keywords FILE]"
---
# Skill: aeo (Answer Engine Optimization)

## What AEO is

Answer Engine Optimization (AEO) is the practice of structuring and formatting
web content so that it can be extracted and surfaced by answer engines — systems
that provide direct answers to queries rather than ranked link lists.

Answer surfaces include:

- **Featured snippets (Position Zero)**: paragraph, list, or table content
  shown above organic results in Google Search.
- **People Also Ask (PAA)**: expandable Q&A boxes in Google SERPs derived
  from related question clusters.
- **Knowledge Panels**: entity information boxes on the right side of SERPs.
- **Voice search results**: single spoken answers from Google Assistant,
  Alexa, Siri, and Cortana.
- **AI Overviews (SGE)**: Google's AI-generated summaries that synthesize
  multiple sources into a single answer block.
- **Bing Copilot answers**: inline answer summaries in Bing's AI-powered
  SERP experience.

AEO is distinct from traditional SEO (which targets ranked link positions) and
GEO (which targets AI citation systems outside search). AEO focuses on the
SERP-level direct-answer surfaces within search engines.

## Featured snippet types and optimal format

Featured snippets are pulled from content on pages that already rank on page 1
for a query. Snippet type determines the optimal content structure:

### Paragraph snippets (most common)

A 40-60 word paragraph answer pulled directly from the page. Google prefers
answers that:

- Start with the defined term or entity name.
- State the definition or answer in the first sentence.
- Follow with 1-2 supporting sentences.
- Avoid bullet points or numbered lists in the answer paragraph itself.

```
Optimal structure:
  H2: What is [term]?
  <p>[Term] is [definition]. [Supporting sentence]. [Optional second sentence].</p>
```

### List snippets (ordered and unordered)

For process or ranked content. Google extracts list items from `<ul>` or `<ol>`
following a heading. Best practices:

- 5-8 items in the list (fewer than 4 or more than 10 reduces eligibility).
- Each item is 4-10 words (concise labels, not full sentences).
- H2 heading ends with a colon or is phrased as "Steps to..." / "Ways to...".
- Do not embed links inside list items that you want featured.

```
Optimal structure:
  H2: Steps to [achieve X]:
  <ol>
    <li>Step one action</li>
    <li>Step two action</li>
    ...
  </ol>
```

### Table snippets

For comparison or structured data. Google extracts tables directly. Best
practices:

- Use semantic `<table>` with `<th>` headers.
- Keep tables to 2-4 columns.
- Row count: 5-10 rows (Google truncates long tables).
- Table caption or preceding heading clearly describes what is compared.

### Video snippets

For how-to or tutorial queries. Requires a YouTube video with timestamps.
Use `Video` schema or YouTube chapter markers. Less relevant for text-content
AEO; included for completeness.

## Snippet eligibility signals

Not all pages can win snippets. Key eligibility signals:

1. **Question-intent keywords**: content must target a question-format query
   (Who, What, When, Where, Why, How, Is, Are, Can, Does).
2. **Clear, concise answer**: the answer paragraph should be 40-60 words.
   Longer answers are less likely to be extracted.
3. **Proper heading structure**: the question as a heading (H2 or H3)
   followed immediately by the answer paragraph.
4. **Page 1 ranking**: Google only pulls snippets from pages that already rank
   in the top 10. Winning a snippet requires first winning a page 1 position.
5. **Content freshness**: recently updated content is preferred for snippets
   on rapidly changing topics.
6. **E-E-A-T signals**: high-authority pages are preferred for medical, legal,
   financial, and scientific snippet content.

## People Also Ask (PAA)

PAA boxes are expandable Q&A accordions that appear mid-SERP. Each click on a
PAA question expands to show a featured snippet-style answer, then adds new
related questions. PAA has dynamic clustering behavior: answering one PAA
question seeds more questions.

### How PAA clusters form

PAA questions are grouped around semantic clusters, not individual keywords.
A page targeting "How to configure a VPN" will surface PAA clusters for:

- "What is a VPN?"
- "How does VPN encryption work?"
- "Is VPN legal?"
- "What is the difference between VPN and proxy?"

Optimize for the cluster, not just the seed query.

### How to capture PAA boxes

1. **Research PAA clusters**: use Semrush, Ahrefs, or the AlsoAsked tool to
   map the question clusters for your topic.
2. **Create FAQ sections**: add a FAQ section at the bottom of each major
   content page addressing the 4-6 most common PAA questions for that topic.
3. **Add FAQPage schema**: markup the FAQ section with FAQPage JSON-LD.
4. **Answer each question in 40-60 words**: use the paragraph snippet format
   for each FAQ answer.
5. **Interlink related FAQ pages**: internal linking within a topic cluster
   strengthens PAA cluster coverage.

### FAQ pages that dominate PAA

Topic-focused FAQ pages that address an entire semantic cluster can capture
5-10 PAA boxes for a single query. Effective FAQ pages:

- Cover 10-20 questions around a coherent topic cluster.
- Use FAQPage + Question + Answer JSON-LD markup.
- Answer each question in 40-60 words (snippet zone).
- Link to deeper content pages for each topic.

## FAQPage schema

The `FAQPage` schema is the most directly impactful AEO structured data type.
It signals to Google which content is intended as a direct answer to a question.

### JSON-LD format

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is the maximum upload size in Contentstack?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Contentstack allows a maximum file upload size of 512 MB per asset. For assets larger than 512 MB, use the Contentstack Management API with chunked upload. Supported file types include images, videos, PDFs, and other binary formats."
      }
    },
    {
      "@type": "Question",
      "name": "How do I enable multi-language content in Contentstack?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Enable multi-language content in Contentstack by adding locales in Stack Settings > Localization. Set a master locale, then enable localization on individual fields in your content type. Publish locale-specific entries through the Localization tab on each entry."
      }
    }
  ]
}
```

### Character limits and what Google surfaces

- Question `name`: 2-90 characters. Google may truncate longer questions in
  the PAA box.
- Answer `text`: 150-600 characters for best display. Answers over 1000
  characters are eligible but may be truncated.
- Google shows a maximum of 3 FAQPage questions in rich results per URL.
- All questions are indexed by Google; only the top 3 are shown visually.
- Duplicate questions across a site reduce eligibility for rich results.

### HowTo schema for process content

For step-by-step procedural content, use `HowTo` instead of `FAQPage`:

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to export content from Contentstack",
  "description": "Step-by-step guide to exporting content types and entries from Contentstack using the CLI.",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Install the Contentstack CLI",
      "text": "Run npm install -g @contentstack/cli to install the Contentstack CLI globally."
    },
    {
      "@type": "HowToStep",
      "name": "Authenticate with your stack",
      "text": "Run csdx auth:login and follow the prompts to authenticate with your Contentstack account and region."
    },
    {
      "@type": "HowToStep",
      "name": "Export content types",
      "text": "Run csdx cm:stacks:export --module content_types to export all content type definitions as JSON files."
    }
  ]
}
```

## Knowledge Panel optimization

Knowledge Panels are entity information boxes that appear on the right side
of Google SERPs for named entities (companies, products, people, places).

### Optimization levers

1. **Google Business Profile**: claim and fully populate the GBP for local
   or service-area businesses. GBP is the strongest Knowledge Panel signal
   for non-Wikipedia entities.
2. **Wikidata entity**: create or claim a Wikidata entity for the
   organization. Wikidata is the primary structured data source for Google
   Knowledge Graph entities.
3. **Wikipedia presence**: a Wikipedia article significantly increases
   Knowledge Panel eligibility. The article must meet Wikipedia's notability
   criteria.
4. **Schema.org Organization with sameAs**: link your site's Organization
   schema to Wikidata, Wikipedia, LinkedIn, and Crunchbase via sameAs.
5. **Consistent NAP**: Name, Address, Phone must be identical across Google
   Business Profile, website, LinkedIn, and any directory listings.
   Inconsistency dilutes entity confidence.
6. **Knowledge Panel claim**: Google allows verified organizations to suggest
   edits to their Knowledge Panel via the "Suggest an edit" interface.

## Voice search readiness

Voice search (Google Assistant, Alexa, Siri) returns a single spoken answer
derived from a featured snippet. Voice-optimized content:

1. **Natural language phrasing**: answers should read naturally when spoken
   aloud. Avoid jargon, abbreviations, or symbols that do not verbalize well.
2. **Conversational question format**: target conversational queries ("How do
   I...?" "What is...?") rather than keyword-only queries.
3. **Local intent signals**: many voice queries have local intent ("near me").
   Ensure NAP consistency and Google Business Profile completeness for
   local voice queries.
4. **Short, direct answers**: 20-30 word answers work best for voice.
   Voice assistants tend to read the first 1-2 sentences of a snippet.
5. **Speakable schema**: `SpeakableSpecification` markup signals which parts
   of a page are optimized for text-to-speech. Primarily relevant for news
   and informational content.

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [".article-headline", ".article-summary"]
  },
  "url": "https://example.com/article"
}
```

## AI Overviews (SGE)

Google's AI Overviews (formerly Search Generative Experience) generates
AI-written summaries that appear above organic results for certain queries.
Sources used in AI Overviews receive a "mini citation" with a favicon and
excerpt.

### What signals favour inclusion in AI Overviews

1. **High E-E-A-T**: Google's E-E-A-T signals (especially first-hand
   experience and expertise) are the primary filter for AI Overview sources.
2. **Structured, factual content**: content with clear headings, numbered
   lists, and specific facts is extracted more readily.
3. **Featured snippet eligibility**: pages that already win featured snippets
   have higher AI Overview inclusion rates.
4. **FAQPage and HowTo schema**: structured data increases AI Overview
   extraction probability for answer content.
5. **HTTPS and Core Web Vitals**: technical quality is a prerequisite.
6. **Author E-E-A-T**: bylined content with author schema (including sameAs
   and credentials) is preferred for YMYL topics.

### Relationship to E-E-A-T

AI Overviews extend E-E-A-T evaluation to include "Experience" (first-hand
accounts, original research, demonstrable expertise). Content that includes:

- Original data or research
- First-person experience statements
- Credentials and author attribution
- Citations of primary sources

...has a measurably higher rate of AI Overview inclusion for expertise-dependent
topics (health, finance, legal, technology).

## CMS implementation notes

### WordPress (Yoast SEO / RankMath)

- Yoast SEO: FAQ block in Gutenberg editor automatically generates FAQPage
  JSON-LD. Use the Yoast FAQ block for all FAQ content.
- RankMath: Schema module supports FAQPage, HowTo, Article schemas from the
  block editor. Enable "Rich Snippet" for each post.
- Custom HowTo: use the RankMath HowTo block or custom Gutenberg block.
- Speakable: neither Yoast nor RankMath generates speakable natively; add via
  custom `wp_head` action.

### Contentstack

- Add a `structured_data` JSON field to every content type.
- For FAQ content types: build a structured field schema with `questions`
  array (question_text + answer_text fields) and serialize to FAQPage JSON-LD
  on the Next.js frontend.
- HowTo: use a `steps` block field (array with title + description fields) and
  serialize to HowTo JSON-LD.
- Inject JSON-LD in the Next.js `<head>` via `next/head` or `<Script>` with
  `type="application/ld+json"`.

### Contentful

- Add a `faqItems` reference field (array of FAQ entry type) for FAQ pages.
- Each FAQ entry has `question` (short text) and `answer` (long text) fields.
- Serialize to FAQPage JSON-LD in the frontend (Next.js, Gatsby).
- For HowTo: a `steps` reference field pointing to a Step content type
  (title + instructionText).

### Drupal / Schema.org module

- Install and configure `schema_metatag` contributed module.
- For FAQPage: create a custom content type "FAQ Item" with question/answer
  fields. Use views to assemble FAQ pages and attach FAQPage schema via the
  schema_metatag module.
- HowTo: `schema_metatag` supports HowTo out of the box; map step fields to
  the module configuration.
- Speakable: custom Drupal hook or Paragraphs component with explicit CSS
  selectors.

### Sitecore

- Add a `StructuredData` JSON rendering to the layout for content types that
  need FAQ or HowTo schema.
- For FAQ content: create a SXA component that reads FAQ datasource items and
  serializes to JSON-LD in the `<head>`.
- Use the SXA Page Metadata rendering for site-wide Organization and WebSite
  schemas.

### Webflow

- Webflow does not generate JSON-LD natively.
- Use Webflow's Custom Code area (Page Settings > Custom Code > `<head>`)
  for per-page JSON-LD injection.
- For collection-driven FAQ pages: use Webflow's embed block with JavaScript
  to generate JSON-LD dynamically from CMS collection fields.
- Devlink (React): inject JSON-LD via Next.js `next/head` in the wrapper
  component.

## AEO audit checklist (output format)

When running an AEO audit, produce a markdown checklist with scores:

```markdown
# AEO Audit: example.com

**Score: 54/100**

## Featured Snippet Eligibility
- [x] Question-format headings present (14/18 sampled pages)
- [ ] Only 4/18 pages have 40-60 word answer paragraphs (snippet zone)
- [ ] 8 pages missing H2 in question format before their answer paragraph

## Schema Coverage
- [x] FAQPage schema found on 3 pages
- [ ] HowTo schema NOT found (site has 6 how-to guides without HowTo schema)
- [ ] Speakable schema NOT present

## Meta Tags and Title Optimization
- [x] All 18 sampled pages have meta descriptions
- [ ] 6 meta descriptions exceed 160 characters
- [ ] 4 title tags start with brand name rather than question/keyword

## Content Structure
- [x] Most H2s are question-format (78%)
- [ ] Average first-paragraph length: 94 words (too long for snippet zone)
- [x] 9 pages have ordered list answers (list snippet candidates)
- [x] 5 pages have table answers (table snippet candidates)

## Recommendations (priority order)
1. Shorten answer paragraphs to 40-60 words on FAQ and definition pages
2. Add HowTo JSON-LD to 6 how-to guides
3. Add FAQPage JSON-LD to all FAQ pages (only 3/12 FAQ pages have it)
4. Rewrite opening paragraphs for question-headed sections to lead with answer
5. Trim meta descriptions over 160 characters
```

## Execution

```bash
python3 "$CLAUDE_SKILL_DIR/aeo_audit.py" $ARGUMENTS
```

### Argument interface

```
Required:
  --url URL           Base URL to audit (e.g. https://example.com)

Optional:
  --pages N           Number of pages to sample beyond homepage (default: 5)
  --output DIR        Output directory for report files (default: ./aeo-output)
  --format FORMAT     Output format: markdown | json | both (default: markdown)
  --keywords FILE     Path to a text file with one keyword/query per line
                      (used to assess heading question coverage)
```

The script produces:
- `aeo-report.md` — human-readable AEO checklist with score and recommendations
- `aeo-data.json` (if --format json or both) — structured audit data
- Exit code 0 = audit complete, exit code 1 = fatal error
