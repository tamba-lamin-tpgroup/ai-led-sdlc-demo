---
name: tech-stack-audit
description: >
  Run a Wappalyzer/BuiltWith-grade technology stack audit on any web property.
  Detects CMS (Drupal, WordPress, and 15+ others), themes, plugins/modules, CSS
  frameworks, JavaScript libraries, third-party services (analytics, CDN, chat,
  ads, video), and HTTP security headers. Works on local (DDEV) and remote targets.
  Outputs a markdown report and structured JSON. Use when asked to fingerprint,
  audit, or inventory the technology stack of any website.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
argument-hint: "--url URL [--pages N] [--local] [--output DIR] [--format markdown|json|both]"
---

# Tech Stack Audit Skill

Runs a Wappalyzer/BuiltWith-grade technology fingerprint against any web property.

## Quick Start

```
/tech-stack-audit --url https://example.com
/tech-stack-audit --url https://mysite.ddev.site --local
/tech-stack-audit --url https://example.com --pages 20 --format both
/tech-stack-audit --url https://example.com --output ./tech-audit
```

## All Options

| Option | Default | Description |
|--------|---------|-------------|
| `--url URL` | **required** | Target URL |
| `--pages N` | 10 | Number of pages to sample for detection |
| `--local` | false | Local/dev site: disable SSL verification |
| `--output DIR` | `./tech-stack-output` | Output directory |
| `--format FORMAT` | `both` | Output format: `markdown`, `json`, or `both` |
| `--user-agent STR` | SEO-Audit-Bot/1.0 | Custom user agent |
| `--timeout N` | 20 | Per-request timeout in seconds |

## Prerequisites

```bash
pip3 install requests beautifulsoup4 lxml --break-system-packages -q
```

## Execution

```bash
python3 "$CLAUDE_SKILL_DIR/tech_stack_audit.py" $ARGUMENTS
```

## What Gets Detected

| Category | Details |
|----------|---------|
| **CMS** | Drupal (version), WordPress (version), Joomla, Magento, Shopify, HubSpot, Ghost, Squarespace, Wix and 30+ DXP/headless platforms — see full list below |
| **Themes / Templates** | Active theme name from CSS/JS paths, admin hints |
| **Plugins / Modules** | Drupal contrib + custom modules, WordPress plugins |
| **CSS Frameworks** | Bootstrap (3/4/5), Tailwind, Foundation, Bulma, Materialize |
| **JavaScript Libraries** | jQuery, React, Vue, Angular, Next.js, Nuxt, HTMX, Alpine.js, D3, GSAP, Lodash, and 20+ more |
| **Analytics** | Google Analytics (UA/GA4), GTM, Adobe Analytics, Matomo, Plausible |
| **CDN & Hosting** | Cloudflare, Fastly, Akamai, AWS CloudFront, Pantheon, Acquia, WP Engine |
| **Chat & Support** | Intercom, Zendesk, Drift, HubSpot Chat, LiveChat |
| **Video** | Brightcove, Vimeo, YouTube embeds, Kaltura, Wistia |
| **Search** | Solr, Elasticsearch, Algolia, SearchWP, Site Search 360 |
| **A11y Tools** | AudioEye, UserWay, accessiBe, EqualWeb |
| **Security Headers** | HSTS, CSP, X-Frame-Options, X-Content-Type, Referrer-Policy, Permissions-Policy |
| **CMS Version Indicators** | Generator meta, admin path patterns, changelog hints, JS/CSS versioned paths |

## Output Files

| File | Description |
|------|-------------|
| `tech-stack-report.md` | Human-readable report with evidence tables |
| `tech-stack-report.json` | Structured detection data for programmatic use |
| `raw-detections.json` | Per-page raw fingerprint data |

## Detected CMS / DXP Platforms (full list)

### Pure-play headless CMS

| Platform | Detection signals |
|---|---|
| Contentful | `images.ctfassets.net` CDN, `ctfl.space` space ID, Delivery API URL |
| Contentstack | `images.contentstack.io` CDN, `cda.contentstack.io`, live-preview attrs |
| Kontent.ai | `kc-usercontent.com` CDN, `deliver.kontent.ai` URL |
| Storyblok | `a.storyblok.com` CDN, `data-blok-c=` attrs, Storyblok Bridge JS |
| Sanity | `cdn.sanity.io`, `sanityClient` JS global, sanity project ID var |
| Amplience | `a.bigcontent.io` CDN, `amplience.net` API domain |
| Agility CMS | `aglty.io` CDN, `static.agilitycms.com`, agilitypreview mode |
| Payload CMS | `/api/payload` path, `@payloadcms` NPM namespace |
| Strapi | Strapi REST API patterns, `strapiMediaUrl` JS var |
| CrafterCMS | `/static-assets/` path, `iceOn` ICE mode, `crafter-page` class |

### DXP / Hybrid platforms

| Platform | Detection signals |
|---|---|
| Sitecore XM Cloud | `edge.sitecorecloud.io`, `sc-jss`, `~/link.aspx`, `data-sc-*` attrs |
| Sitecore XP | `sitecore/shell`, `xDB` marker, Sitecore domain |
| Optimizely CMS (Episerver) | `episerver` JS, `EPiServer` namespace, `/link/{guid}` URLs |
| Bloomreach | `brxm` marker, `bloomreach.io` API, `br-page-meta` |
| Magnolia DX Core | `mgnl:` namespace, `x-magnolia-` header, `magnoliaContext` JS |
| Liferay DXP | `Liferay.AUI` JS, `/o/frontend-js-web/` path, `Liferay.authToken` |
| Kentico Xperience | `KenticoAdminToolbar`, `CMSEditableRegion`, `ktc-` class prefix |
| Umbraco | `/media/{id}/` URLs, `umb-block-list`, `x-umbraco-` header |
| Webflow | `assets.website-files.com` CDN, `data-wf-*` attrs, `w-nav` class |
| dotCMS | `/contentAsset/` path, `/dA/` path, `dotcms` class |
| Pimcore | `pimcore-editable` attr, `bundles/pimcorecore`, `x-pimcore-` header |
| Progress Sitefinity | `sitefinity` class, Telerik components, `/Sitefinity/` admin path |
| HCL Digital Experience | `/wps/portal` path, `/wps/wcm/` WCM path, `PortalServer` marker |
| CoreMedia Content Cloud | `cm-richtext` class, `coremedia:///cap/` internal URLs |
| Squiz Matrix | `/__data/assets/` path, `SQ_BACKEND` marker, `x-squiz-` header |

### Traditional open-source CMS (enhanced)

| Platform | Detection signals |
|---|---|
| Drupal (Acquia) | Generator meta, `/sites/default/files/`, `data-drupal-*`, `drupal-settings-json` |
| WordPress | Generator meta, `/wp-content/`, `wp-json`, `wpemoji` |
| Joomla | Generator meta, `/media/jui/`, `/components/com_` |

## Sample Output (markdown)

```
## CMS
- Drupal 10.x (confidence: HIGH) — detected via: generator meta, /core/ asset paths, data-drupal-* attributes

## JavaScript Libraries
- jQuery 3.6.4 — /sites/default/files/js/jquery.min.js?v=3.6.4
- React 18.2.0 — /static/js/main.chunk.js (React DevTools hint)
...
```
