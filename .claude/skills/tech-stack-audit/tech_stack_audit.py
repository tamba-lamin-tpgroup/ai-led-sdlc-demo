"""
Generic Technology Stack Audit.

Wappalyzer/BuiltWith-grade detection for any web property.
Detects CMS, themes, plugins, JS/CSS frameworks, third-party services,
and HTTP security headers across a configurable page sample.

Usage:
    python3 tech_stack_audit.py --url https://example.com
    python3 tech_stack_audit.py --url https://mysite.ddev.site --local
    python3 tech_stack_audit.py --url https://example.com --pages 20 --format both
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Detection rules — pattern: (name, confidence, evidence_template)
# ---------------------------------------------------------------------------

CMS_PATTERNS: list[tuple[str, str, list[tuple[str, str]]]] = [
    # -----------------------------------------------------------------------
    # Open-source traditional CMS
    # -----------------------------------------------------------------------
    ("Drupal", "HTML", [
        (r'<meta name="Generator" content="Drupal ?([\d.]+)', "Generator meta"),
        (r'/sites/(default|all)/files/', "Drupal files path"),
        (r'/core/misc/drupal\.js', "Drupal core JS"),
        (r'data-drupal-', "Drupal data attributes"),
        (r'Drupal\.settings', "Drupal.settings JS"),
        (r'drupal-settings-json', "Drupal settings JSON attr"),
        (r'x-generator.*Drupal', "X-Generator header"),
    ]),
    ("WordPress", "HTML", [
        (r'/wp-content/(themes|plugins|uploads)/', "WP content path"),
        (r'<meta name=["\']generator["\'] content=["\']WordPress ([\d.]+)', "WP generator meta"),
        (r'wp-json', "WP REST API endpoint"),
        (r'wp-includes/', "WP includes path"),
        (r'wpemoji', "WP emoji detection JS"),
    ]),
    ("Joomla", "HTML", [
        (r'<meta name="generator" content="Joomla', "Joomla generator"),
        (r'/media/jui/', "Joomla UI path"),
        (r'/components/com_', "Joomla component path"),
    ]),
    ("Shopify", "HTML", [
        (r'cdn\.shopify\.com', "Shopify CDN"),
        (r'Shopify\.theme', "Shopify theme JS"),
        (r'myshopify\.com', "Shopify domain"),
    ]),
    ("Magento", "HTML", [
        (r'/skin/frontend/', "Magento skin path"),
        (r'Mage\.Cookies', "Magento cookies JS"),
        (r'/pub/static/', "Magento pub/static path"),
        (r'MAGE_URLS', "Magento URLs JS"),
    ]),
    ("HubSpot CMS", "HTML", [
        (r'js\.hs-scripts\.com', "HubSpot script"),
        (r'hs-analytics', "HubSpot analytics"),
        (r'hsforms\.com', "HubSpot forms CDN"),
    ]),
    ("Squarespace", "HTML", [
        (r'squarespace\.com', "Squarespace URL"),
        (r'Static\.SQUARESPACE_CONTEXT', "Squarespace context JS"),
        (r'squarespace-cdn\.com', "Squarespace CDN"),
    ]),
    ("Wix", "HTML", [
        (r'wixstatic\.com', "Wix static CDN"),
        (r'X-Wix-', "Wix response headers"),
        (r'wix-bolt', "Wix Bolt framework"),
    ]),
    ("Ghost", "HTML", [
        (r'/ghost/', "Ghost admin path"),
        (r'"@context":"https://schema.org","@type":"Article".*ghost', "Ghost schema"),
        (r'ghost-sdk', "Ghost SDK"),
    ]),
    # -----------------------------------------------------------------------
    # Pure-play headless CMS
    # -----------------------------------------------------------------------
    ("Contentful", "HTML", [
        (r'contentful\.com', "Contentful API URL"),
        (r'ctfl\.space', "Contentful space ID"),
        (r'images\.ctfassets\.net', "Contentful Assets CDN"),
        (r'downloads\.ctfassets\.net', "Contentful Downloads CDN"),
        (r'assets\.ctfassets\.net', "Contentful Assets CDN v2"),
    ]),
    ("Contentstack", "HTML", [
        (r'contentstack\.com', "Contentstack API URL"),
        (r'images\.contentstack\.io', "Contentstack Images CDN"),
        (r'eu-images\.contentstack\.com', "Contentstack EU CDN"),
        (r'cda\.contentstack\.io', "Contentstack Delivery API"),
        (r'data-pageref.*contentstack', "Contentstack Live Preview"),
    ]),
    ("Kontent.ai", "HTML", [
        (r'preview-assets-us-01\.kc-usercontent\.com', "Kontent.ai Preview CDN"),
        (r'assets-us-01\.kc-usercontent\.com', "Kontent.ai Assets CDN"),
        (r'deliver\.kontent\.ai', "Kontent.ai Delivery API"),
        (r'kontent\.ai', "Kontent.ai domain reference"),
    ]),
    ("Storyblok", "HTML", [
        (r'a\.storyblok\.com', "Storyblok Assets CDN"),
        (r'img2\.storyblok\.com', "Storyblok Image Service"),
        (r'app\.storyblok\.com', "Storyblok app reference"),
        (r'storyblok-sdk-0\.1', "Storyblok Bridge JS"),
        (r'data-blok-c=', "Storyblok blok attr"),
        (r'sb-edit', "Storyblok edit mode CSS"),
    ]),
    ("Sanity", "HTML", [
        (r'cdn\.sanity\.io', "Sanity CDN"),
        (r'sanity\.io/images', "Sanity image CDN"),
        (r'sanityClient', "Sanity client JS"),
        (r'@sanity/client', "Sanity client NPM"),
        (r'sanityProjectId', "Sanity project ID JS"),
        (r'useSanityClient', "Sanity React hook"),
    ]),
    ("Amplience", "HTML", [
        (r'a\.bigcontent\.io', "Amplience Assets CDN"),
        (r'amplience\.net', "Amplience API domain"),
        (r'cdn\.media\.amplience\.net', "Amplience Media CDN"),
        (r'Dynamic-Content', "Amplience Dynamic Content header"),
        (r'dc-cdn\.com', "Amplience DC CDN"),
    ]),
    # -----------------------------------------------------------------------
    # Hybrid and DXP platforms
    # -----------------------------------------------------------------------
    ("Bloomreach", "HTML", [
        (r'brxm', "Bloomreach XM marker"),
        (r'bloomreach\.io', "Bloomreach API domain"),
        (r'bloomreach-page', "Bloomreach Page context"),
        (r'x-bloomreach-', "Bloomreach response header"),
        (r'hippobrokenlink', "Bloomreach broken link CSS"),
        (r'channel-manager', "Bloomreach Channel Manager"),
        (r'br-page-meta', "Bloomreach Page meta"),
    ]),
    ("Optimizely CMS", "HTML", [
        (r'episerver', "Episerver/Optimizely JS"),
        (r'epi\.ready', "Episerver ready event"),
        (r'EPiServer', "EPiServer namespace"),
        (r'optimizely\.com/contentmanagement', "Optimizely CMS reference"),
        (r'episervercms', "Episerver CMS class"),
        (r'/link/[0-9a-f]{32}', "Optimizely internal link"),
        (r'epi-quickNavigator', "Episerver toolbar"),
    ]),
    ("Sitecore XM Cloud", "HTML", [
        (r'sitecore', "Sitecore class/attr"),
        (r'sc_site', "Sitecore site param"),
        (r'-/media/', "Sitecore media path"),
        (r'~/link\.aspx', "Sitecore link handler"),
        (r'data-sc-', "Sitecore data attributes"),
        (r'sc-jss', "Sitecore JSS"),
        (r'jss-server-rendering', "Sitecore JSS rendering"),
        (r'scjss', "Sitecore JSS bundle"),
        (r'edge\.sitecorecloud\.io', "Sitecore Experience Edge"),
        (r'x-sitecore-', "Sitecore response header"),
    ]),
    ("Sitecore XP", "HTML", [
        (r'sitecore/shell', "Sitecore shell path"),
        (r'xDB', "Sitecore xDB marker"),
        (r'sitecore\.net', "Sitecore domain"),
        (r'SITECORE_DIST_PATH', "Sitecore dist path"),
    ]),
    ("Magnolia", "HTML", [
        (r'mgnl:', "Magnolia namespace prefix"),
        (r'magnolia\.cms', "Magnolia CMS package"),
        (r'\.mgnl-', "Magnolia class prefix"),
        (r'x-magnolia-', "Magnolia response header"),
        (r'magnoliaContext', "Magnolia context JS"),
        (r'magnolia-rest-api', "Magnolia REST API"),
    ]),
    ("Liferay DXP", "HTML", [
        (r'liferay', "Liferay class/attr"),
        (r'Liferay\.AUI', "Liferay AlloyUI"),
        (r'/o/frontend-js-web/', "Liferay frontend JS"),
        (r'liferay-ui:', "Liferay UI tag"),
        (r'Liferay\.authToken', "Liferay auth token JS"),
        (r'/web/guest/', "Liferay default web path"),
        (r'PortalUtil', "Liferay portal utility"),
    ]),
    ("Kentico Xperience", "HTML", [
        (r'KenticoAdminToolbar', "Kentico admin toolbar"),
        (r'kentico', "Kentico class/marker"),
        (r'Kentico\.Components', "Kentico components"),
        (r'xperience', "Kentico Xperience class"),
        (r'ktc-', "Kentico class prefix"),
        (r'CMSEditableRegion', "Kentico editable region"),
        (r'CMSPageWrapper', "Kentico page wrapper"),
    ]),
    ("Umbraco", "HTML", [
        (r'umbraco', "Umbraco class/attr"),
        (r'/media/\d+/[^"\']+', "Umbraco media URL"),
        (r'UmbracoCanonicalUrl', "Umbraco canonical"),
        (r'umb-block-list', "Umbraco Block List"),
        (r'x-umbraco-', "Umbraco response header"),
        (r'UmbracoApiController', "Umbraco API controller"),
        (r'umbracoNaviHide', "Umbraco hide from nav"),
    ]),
    ("Webflow", "HTML", [
        (r'webflow\.com/js', "Webflow JS"),
        (r'data-wf-', "Webflow data attrs"),
        (r'global-webflow\.css', "Webflow global CSS"),
        (r'uploads-ssl\.webflow\.com', "Webflow uploads CDN"),
        (r'assets\.website-files\.com', "Webflow assets CDN"),
        (r'w-nav', "Webflow nav class"),
        (r'w-container', "Webflow container class"),
    ]),
    ("Strapi", "HTML", [
        (r'strapi', "Strapi class/attr"),
        (r'/api/[a-z-]+\?populate', "Strapi REST API pattern"),
        (r'strapi\.io', "Strapi domain reference"),
        (r'strapiMediaUrl', "Strapi media URL JS"),
        (r'/_next/.*strapi', "Next.js with Strapi pattern"),
    ]),
    ("Payload CMS", "HTML", [
        (r'payload-cms', "Payload CMS class"),
        (r'/api/payload', "Payload CMS API path"),
        (r'@payloadcms', "Payload CMS NPM namespace"),
        (r'payloadConfig', "Payload config JS"),
    ]),
    ("Agility CMS", "HTML", [
        (r'aglty\.io', "Agility CMS CDN"),
        (r'static\.agilitycms\.com', "Agility CMS static CDN"),
        (r'agilitycms', "Agility CMS marker"),
        (r'agilitypreview', "Agility Preview mode"),
    ]),
    ("dotCMS", "HTML", [
        (r'dotcms', "dotCMS class/attr"),
        (r'/contentAsset/', "dotCMS content asset path"),
        (r'/dA/', "dotCMS direct asset path"),
        (r'dot_object', "dotCMS object JS"),
        (r'x-powered-by.*dotcms', "dotCMS powered-by header"),
        (r'dotEditPage', "dotCMS edit mode"),
    ]),
    ("CrafterCMS", "HTML", [
        (r'craftercms', "CrafterCMS class/attr"),
        (r'crafter-page', "CrafterCMS page class"),
        (r'/static-assets/', "CrafterCMS static assets path"),
        (r'iceOn', "CrafterCMS ICE mode"),
        (r'crafter-studio', "Crafter Studio"),
        (r'crafterConf', "CrafterCMS config JS"),
    ]),
    ("Pimcore", "HTML", [
        (r'pimcore', "Pimcore class/attr"),
        (r'/pimcore/', "Pimcore path"),
        (r'pimcore-editable', "Pimcore editable attr"),
        (r'pimcore-tag-', "Pimcore tag class"),
        (r'bundles/pimcorecore', "Pimcore core bundle"),
        (r'x-pimcore-', "Pimcore response header"),
    ]),
    ("Progress Sitefinity", "HTML", [
        (r'sitefinity', "Sitefinity class/marker"),
        (r'Telerik', "Telerik/Progress UI component"),
        (r'sfPageEditor', "Sitefinity page editor"),
        (r'sf-backend-wrp', "Sitefinity backend wrapper"),
        (r'SitefinityWebApp', "Sitefinity web app"),
        (r'x-sf-', "Sitefinity response header"),
        (r'/Sitefinity/', "Sitefinity admin path"),
    ]),
    ("HCL Digital Experience", "HTML", [
        (r'wps/portal', "WebSphere Portal path"),
        (r'/wps/wcm/', "WCM content path"),
        (r'com\.ibm\.lotus\.domino', "IBM Domino reference"),
        (r'HCL Digital Experience', "HCL DX meta"),
        (r'PortalServer', "Portal server marker"),
        (r'hcl-dx', "HCL DX class"),
        (r'LotusHeader', "Lotus/HCL header class"),
    ]),
    ("CoreMedia Content Cloud", "HTML", [
        (r'coremedia', "CoreMedia class/attr"),
        (r'cm-richtext', "CoreMedia richtext class"),
        (r'coremedia:///cap/', "CoreMedia internal URL"),
        (r'CoreMedia', "CoreMedia JS namespace"),
        (r'/blueprint/', "CoreMedia Blueprint template path"),
        (r'cm-image', "CoreMedia image class"),
    ]),
    ("Squiz Matrix", "HTML", [
        (r'squiz\.net', "Squiz domain"),
        (r'squiz-matrix', "Squiz Matrix class"),
        (r'matrix-asset-url', "Squiz Matrix asset URL"),
        (r'/__data/assets/', "Squiz Matrix asset path"),
        (r'SQ_BACKEND', "Squiz backend marker"),
        (r'squizmap', "Squiz map class"),
        (r'x-squiz-', "Squiz response header"),
    ]),
]

CSS_FRAMEWORKS: list[tuple[str, list[str]]] = [
    ("Bootstrap 5", [r"bootstrap(?:\.min)?\.css\?v?5", r"bootstrap@5", r"btn-primary.*bs5"]),
    ("Bootstrap 4", [r"bootstrap(?:\.min)?\.css\?v?4", r"bootstrap@4"]),
    ("Bootstrap 3", [r"bootstrap(?:\.min)?\.css\?v?3", r"bootstrap@3"]),
    ("Tailwind CSS", [r"tailwind", r"tailwindcss"]),
    ("Foundation", [r"foundation(?:\.min)?\.css", r"foundation\.js"]),
    ("Bulma", [r"bulma(?:\.min)?\.css"]),
    ("Materialize", [r"materialize(?:\.min)?\.css"]),
    ("UIkit", [r"uikit(?:\.min)?\.css"]),
]

JS_LIBRARIES: list[tuple[str, list[str]]] = [
    ("jQuery", [r"jquery(?:\.min)?\.js", r"jquery[/-]([\d.]+)"]),
    ("React", [r"react(?:\.production|\.development)?\.min\.js", r"react-dom", r"__reactFiber"]),
    ("Vue.js", [r"vue(?:\.min)?\.js", r"vue@[\d.]", r"__vue__"]),
    ("Angular", [r"angular(?:\.min)?\.js", r"@angular/core"]),
    ("Next.js", [r"_next/static", r"next/dist"]),
    ("Nuxt.js", [r"_nuxt/", r"nuxt\.config"]),
    ("Alpine.js", [r"alpinejs", r"x-data="]),
    ("HTMX", [r"htmx(?:\.min)?\.js", r"hx-get="]),
    ("D3.js", [r"d3(?:\.min)?\.js", r"d3@[\d.]"]),
    ("GSAP", [r"gsap(?:\.min)?\.js", r"TweenMax"]),
    ("Lodash", [r"lodash(?:\.min)?\.js", r"_\.debounce"]),
    ("Moment.js", [r"moment(?:\.min)?\.js"]),
    ("Chart.js", [r"chart(?:\.min)?\.js", r"Chart\.register"]),
    ("Swiper", [r"swiper(?:\.min)?\.js", r"swiper/dist"]),
    ("Slick Carousel", [r"slick(?:\.min)?\.js", r"slick-carousel"]),
    ("Select2", [r"select2(?:\.min)?\.js"]),
    ("DataTables", [r"dataTables(?:\.min)?\.js"]),
    ("Leaflet", [r"leaflet(?:\.min)?\.js"]),
    ("Three.js", [r"three(?:\.min)?\.js", r"THREE\."]),
    ("Axios", [r"axios(?:\.min)?\.js"]),
]

THIRD_PARTY_SERVICES: list[tuple[str, str, list[str]]] = [
    ("Google Analytics (GA4)", "Analytics", [r"googletagmanager\.com/gtag", r"gtag\('config'"]),
    ("Google Analytics (UA)", "Analytics", [r"google-analytics\.com/analytics\.js", r"ga\('create'"]),
    ("Google Tag Manager", "Tag Management", [r"googletagmanager\.com/gtm"]),
    ("Adobe Analytics", "Analytics", [r"omtrdc\.net", r"s\.t\(\)"]),
    ("Matomo", "Analytics", [r"matomo(?:\.js|\.php)", r"_paq\.push"]),
    ("Plausible", "Analytics", [r"plausible\.io/js"]),
    ("Cloudflare", "CDN/Security", [r"cdnjs\.cloudflare\.com", r"cf-ray", r"__cf_bm"]),
    ("AWS CloudFront", "CDN", [r"cloudfront\.net"]),
    ("Fastly", "CDN", [r"fastly\.com", r"fastly-io"]),
    ("Akamai", "CDN", [r"akamaized\.net", r"akamai\.com"]),
    ("Pantheon", "Hosting", [r"pantheonsite\.io", r"x-styx-", r"pagescdn\.com"]),
    ("Acquia", "Hosting", [r"acquia-sites\.com", r"acquiacloud\.com"]),
    ("WP Engine", "Hosting", [r"wpengine\.com"]),
    ("Intercom", "Chat", [r"intercomcdn\.com", r"intercom\.io/api"]),
    ("Zendesk", "Chat/Support", [r"zopim\.com", r"zendesk\.com/embeddable_framework"]),
    ("HubSpot", "Marketing/CRM", [r"js\.hs-scripts\.com", r"hs-analytics"]),
    ("Salesforce Pardot", "Marketing", [r"pardot\.com", r"pi\.pardot\.com"]),
    ("Marketo", "Marketing", [r"marketo\.com/js/forms2"]),
    ("OneTrust", "Cookie Consent", [r"onetrust\.com", r"optanon"]),
    ("Cookiebot", "Cookie Consent", [r"cookiebot\.com"]),
    ("YouTube", "Video", [r"youtube\.com/embed", r"youtube-nocookie\.com"]),
    ("Vimeo", "Video", [r"player\.vimeo\.com", r"vimeocdn\.com"]),
    ("Brightcove", "Video", [r"brightcove\.com", r"brightcove\.net"]),
    ("Kaltura", "Video", [r"kaltura\.com"]),
    ("Wistia", "Video", [r"wistia\.com", r"wistia\.net"]),
    ("Algolia", "Search", [r"algolia\.net", r"algoliainsights"]),
    ("Elasticsearch/Elastic", "Search", [r"elastic\.co"]),
    ("Yext", "Local Search", [r"yext\.com"]),
    ("AudioEye", "Accessibility", [r"audioeye\.com"]),
    ("UserWay", "Accessibility", [r"userway\.org"]),
    ("accessiBe", "Accessibility", [r"acsbapp\.com"]),
    ("EqualWeb", "Accessibility", [r"equalweb\.com"]),
    ("Google Fonts", "Fonts", [r"fonts\.googleapis\.com", r"fonts\.gstatic\.com"]),
    ("Typekit / Adobe Fonts", "Fonts", [r"use\.typekit\.net", r"typekit\.com"]),
    ("Font Awesome", "Icons", [r"fontawesome\.com", r"fa-"]),
    ("reCAPTCHA", "Security", [r"google\.com/recaptcha", r"recaptcha\.net"]),
    ("hCaptcha", "Security", [r"hcaptcha\.com"]),
    ("Sentry", "Error Tracking", [r"sentry\.io", r"browser\.sentry-cdn\.com"]),
    ("Hotjar", "Analytics/UX", [r"hotjar\.com"]),
    ("FullStory", "Analytics/UX", [r"fullstory\.com"]),
    ("DataDome", "Bot Protection", [r"datadome\.co", r"dd-cdn\.com"]),
    ("Cloudflare Bot Mgmt", "Bot Protection", [r"challenges\.cloudflare\.com"]),
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "X-XSS-Protection",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
]

DRUPAL_MODULES: list[tuple[str, str]] = [
    ("Metatag", r"/metatag/"),
    ("Pathauto", r"/pathauto/"),
    ("Token", r"/token/"),
    ("Views", r"/views/"),
    ("Redirect", r"/redirect/"),
    ("Simple XML Sitemap", r"/simple_sitemap/"),
    ("Webform", r"/webform/"),
    ("Media", r"/media/"),
    ("Entity Reference", r"/entity_reference/"),
    ("CKEditor", r"/ckeditor/"),
    ("Paragraphs", r"/paragraphs/"),
    ("Field Group", r"/field_group/"),
    ("Address", r"/address/"),
    ("Admin Toolbar", r"/admin_toolbar/"),
    ("Devel", r"/devel/"),
    ("Colorbox", r"/colorbox/"),
    ("Focal Point", r"/focal_point/"),
    ("Layout Builder", r"/layout_builder/"),
    ("Schema.org Metatag", r"/schema_metatag/"),
    ("Search API", r"/search_api/"),
    ("Facets", r"/facets/"),
    ("Solr Search", r"/solr/"),
]

WORDPRESS_PLUGINS: list[tuple[str, str]] = [
    ("Yoast SEO", r"/yoast-seo/|/wordpress-seo/"),
    ("RankMath", r"/rank-math/"),
    ("WooCommerce", r"/woocommerce/"),
    ("Elementor", r"/elementor/"),
    ("Jetpack", r"/jetpack/"),
    ("Contact Form 7", r"/contact-form-7/"),
    ("Gravity Forms", r"/gravityforms/"),
    ("ACF", r"/advanced-custom-fields/"),
    ("WPML", r"/wpml/"),
    ("WP Super Cache", r"/wp-super-cache/"),
    ("Wordfence", r"/wordfence/"),
    ("WP Rocket", r"/wp-rocket/"),
]


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="Technology Stack Audit",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--url", required=True)
    p.add_argument("--pages", type=int, default=10, help="Pages to sample")
    p.add_argument("--local", action="store_true", help="Disable SSL verification")
    p.add_argument("--output", default="./tech-stack-output")
    p.add_argument("--format", choices=["markdown", "json", "both"], default="both")
    p.add_argument("--user-agent", default="SEO-Audit-Bot/1.0 (tech-audit)")
    p.add_argument("--timeout", type=int, default=20)
    return p


# ---------------------------------------------------------------------------
# Detection engine
# ---------------------------------------------------------------------------

def detect_cms(html: str, headers: dict) -> list[dict]:
    detections = []
    combined = html + str(headers)
    for cms_name, _, patterns in CMS_PATTERNS:
        for pattern, evidence_desc in patterns:
            m = re.search(pattern, combined, re.I | re.S)
            if m:
                version = m.group(1) if m.lastindex else ""
                detections.append({
                    "name": cms_name,
                    "version": version,
                    "evidence": evidence_desc,
                    "confidence": "HIGH" if evidence_desc.endswith("meta") else "MEDIUM",
                })
                break  # One match per CMS is enough
    return detections


def detect_css_frameworks(html: str) -> list[dict]:
    results = []
    for fw_name, patterns in CSS_FRAMEWORKS:
        for pat in patterns:
            if re.search(pat, html, re.I):
                results.append({"name": fw_name, "evidence": pat})
                break
    return results


def detect_js_libraries(html: str) -> list[dict]:
    results = []
    for lib_name, patterns in JS_LIBRARIES:
        for pat in patterns:
            if re.search(pat, html, re.I):
                results.append({"name": lib_name, "evidence": pat})
                break
    return results


def detect_third_party(html: str) -> list[dict]:
    results = []
    for svc_name, category, patterns in THIRD_PARTY_SERVICES:
        for pat in patterns:
            if re.search(pat, html, re.I):
                results.append({"name": svc_name, "category": category, "evidence": pat})
                break
    return results


def detect_cms_plugins(html: str, cms: str) -> list[dict]:
    results = []
    plugin_list = DRUPAL_MODULES if cms == "Drupal" else WORDPRESS_PLUGINS if cms == "WordPress" else []
    for plugin_name, pattern in plugin_list:
        if re.search(pattern, html, re.I):
            results.append({"name": plugin_name})
    return results


def audit_security_headers(headers: dict) -> list[dict]:
    results = []
    for h in SECURITY_HEADERS:
        val = headers.get(h, headers.get(h.lower(), ""))
        results.append({
            "header": h,
            "present": bool(val),
            "value": val[:200] if val else "MISSING",
        })
    return results


def sample_pages(base_url: str, session, n: int) -> list[str]:
    """Collect up to n pages from sitemap or homepage links."""
    pages = [base_url]
    try:
        sm = session.get(base_url.rstrip("/") + "/sitemap.xml", timeout=15)
        if sm.status_code == 200:
            found = re.findall(r"<loc>(https?://[^<]+)</loc>", sm.text)
            base_host = urlparse(base_url).netloc
            for u in found:
                if urlparse(u).netloc == base_host and u not in pages:
                    pages.append(u)
                    if len(pages) >= n:
                        break
    except Exception:
        pass
    if len(pages) < n:
        try:
            r = session.get(base_url, timeout=15)
            soup = BeautifulSoup(r.text, "lxml")
            base_host = urlparse(base_url).netloc
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("/"):
                    href = base_url.rstrip("/") + href
                if urlparse(href).netloc == base_host and href not in pages:
                    pages.append(href)
                    if len(pages) >= n:
                        break
        except Exception:
            pass
    return pages[:n]


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def write_markdown(results: dict, out_dir: str, audit_date: str) -> None:
    path = os.path.join(out_dir, "tech-stack-report.md")

    def _table(rows, cols):
        lines = ["| " + " | ".join(cols) + " |",
                 "|" + "|".join(["---"] * len(cols)) + "|"]
        for row in rows:
            lines.append("| " + " | ".join(str(row.get(c, "")) for c in cols) + " |")
        return "\n".join(lines)

    sections = [
        f"# Technology Stack Audit\n",
        f"**Target:** {results['target']}  ",
        f"**Date:** {audit_date}  ",
        f"**Pages Sampled:** {results['pages_sampled']}\n",
        "---\n",
    ]

    if results.get("cms"):
        sections.append("## CMS\n")
        for d in results["cms"]:
            ver = f" {d['version']}" if d.get("version") else ""
            sections.append(f"- **{d['name']}{ver}** (confidence: {d.get('confidence', 'MEDIUM')}) — {d['evidence']}\n")

    if results.get("plugins"):
        cms_name = results["cms"][0]["name"] if results.get("cms") else "CMS"
        sections.append(f"## {cms_name} Plugins / Modules\n")
        for p in results["plugins"]:
            sections.append(f"- {p['name']}\n")

    if results.get("css_frameworks"):
        sections.append("## CSS Frameworks\n")
        for f in results["css_frameworks"]:
            sections.append(f"- {f['name']}\n")

    if results.get("js_libraries"):
        sections.append("## JavaScript Libraries\n")
        for lib in results["js_libraries"]:
            sections.append(f"- {lib['name']}\n")

    if results.get("third_party"):
        sections.append("## Third-Party Services\n")
        by_category: dict[str, list[str]] = defaultdict(list)
        for svc in results["third_party"]:
            by_category[svc["category"]].append(svc["name"])
        for cat, svcs in sorted(by_category.items()):
            sections.append(f"### {cat}\n")
            for s in svcs:
                sections.append(f"- {s}\n")

    if results.get("security_headers"):
        sections.append("## HTTP Security Headers\n")
        present = [h for h in results["security_headers"] if h["present"]]
        missing = [h for h in results["security_headers"] if not h["present"]]
        sections.append(f"**Present:** {len(present)}/{len(results['security_headers'])}\n")
        for h in present:
            sections.append(f"- {h['header']}: `{h['value'][:80]}`\n")
        if missing:
            sections.append(f"\n**Missing:**\n")
            for h in missing:
                sections.append(f"- {h['header']}\n")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(sections))
    print(f"Wrote markdown report: {path}")


def write_json(results: dict, out_dir: str) -> None:
    path = os.path.join(out_dir, "tech-stack-report.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, default=str)
    print(f"Wrote JSON report: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = build_parser().parse_args()
    out_dir = os.path.expanduser(args.output)
    os.makedirs(out_dir, exist_ok=True)
    audit_date = datetime.now().strftime("%Y-%m-%d")

    sess = requests.Session()
    sess.headers.update({"User-Agent": args.user_agent})
    if args.local:
        import urllib3
        urllib3.disable_warnings()
        sess.verify = False

    try:
        r = sess.get(args.url, timeout=args.timeout)
        if r.status_code not in (200, 301, 302):
            sys.exit(f"Site not reachable: {args.url} -> {r.status_code}")
    except Exception as exc:
        sys.exit(f"Cannot reach {args.url}: {exc}")

    print(f"Sampling {args.pages} pages from {args.url}...")
    pages = sample_pages(args.url, sess, args.pages)
    print(f"  Found {len(pages)} pages to analyze")

    # Aggregate detection data across all sampled pages
    all_html = ""
    all_headers: dict = {}
    raw_per_page = []

    for url in pages:
        try:
            resp = sess.get(url, timeout=args.timeout, allow_redirects=True)
            if resp.status_code == 200:
                all_html += resp.text
                all_headers.update(dict(resp.headers))
                raw_per_page.append({"url": url, "status": resp.status_code,
                                     "content_length": len(resp.text)})
        except Exception:
            pass
        time.sleep(0.1)

    print("Running detection engine...")
    cms_detections = detect_cms(all_html, all_headers)
    detected_cms = cms_detections[0]["name"] if cms_detections else "generic"
    plugins = detect_cms_plugins(all_html, detected_cms)
    css_fw = detect_css_frameworks(all_html)
    js_libs = detect_js_libraries(all_html)
    third_party = detect_third_party(all_html)
    # Use last-page headers for security header check
    last_resp_headers: dict = {}
    for url in pages[-1:]:
        try:
            last_resp_headers = dict(sess.head(url, timeout=args.timeout).headers)
        except Exception:
            pass
    sec_headers = audit_security_headers(last_resp_headers or all_headers)

    results = {
        "target": args.url,
        "audit_date": audit_date,
        "pages_sampled": len(pages),
        "cms": cms_detections,
        "plugins": plugins,
        "css_frameworks": css_fw,
        "js_libraries": js_libs,
        "third_party": third_party,
        "security_headers": sec_headers,
        "raw_pages": raw_per_page,
    }

    # Save raw per-page data
    raw_path = os.path.join(out_dir, "raw-detections.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw_per_page, fh, indent=2)

    if args.format in ("markdown", "both"):
        write_markdown(results, out_dir, audit_date)
    if args.format in ("json", "both"):
        write_json(results, out_dir)

    print(f"\n=== Tech Stack Audit Summary ===")
    print(f"  CMS detected      : {', '.join(d['name'] for d in cms_detections) or 'Unknown'}")
    print(f"  Plugins/Modules   : {len(plugins)}")
    print(f"  CSS Frameworks    : {len(css_fw)}")
    print(f"  JS Libraries      : {len(js_libs)}")
    print(f"  Third-party svcs  : {len(third_party)}")
    print(f"  Security headers  : {sum(1 for h in sec_headers if h['present'])}/{len(sec_headers)} present")
    print(f"  Output dir        : {out_dir}")


if __name__ == "__main__":
    main()
