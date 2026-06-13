---

name: accessibility-testing
description: Run automated accessibility checks with Playwright + @axe-core/playwright against WCAG 2.2 Level AA. Mirrors the a11y.yml CI gate, which fails on serious or critical violations across the five smoke routes. Pairs with manual review for what automation cannot detect.
triggers:
  - "accessibility"
  - "a11y"
  - "WCAG"
  - "screen reader"
  - "keyboard navigation"
  - "aria"
  - "axe-core"
  - "color contrast"
  - "focus order"
  - "wcag 2.2"
  - "reduced motion"
context: fork
allowed-tools:
  - Bash
  - Read
argument-hint: "[<route> | <spec-path>]"
---
# Skill: accessibility-testing

WCAG 2.2 Level AA compliance is a release gate for Salone Explorer.
Automation catches a portion of issues; the rest needs manual review.
This skill nails the automatable part. Tooling: Playwright +
`@axe-core/playwright`.

## The CI gate (a11y.yml)

The `a11y.yml` workflow runs the Playwright + axe smoke across FIVE
routes and FAILS the build on any serious or critical violation:

- `/`
- `/attractions/tiwai-island`
- `/about`
- `/signin`
- `/signup`

Every new route or interactive component adds or extends a smoke test
in `tests/a11y/`. See `.claude/rules/test-conventions.md`.

## What automation catches

- Colour contrast - verified against the rendered background, whose
  values derive from the design tokens in `src/styles/tokens.css`.
- Missing alt attributes on images.
- Form fields without labels (sign-in / sign-up forms especially).
- Heading hierarchy skips.
- Empty buttons / links.
- ARIA roles used incorrectly; duplicate IDs; page language not set.

## What automation does NOT catch (manual review)

- Whether alt text actually describes the image.
- Whether heading text is meaningful.
- Whether keyboard navigation and focus order are logical.
- Whether screen-reader announcements are useful.
- Cognitive load and copy clarity.

## Coverage to assert

- **Keyboard nav and focus order:** every interactive element reachable
  by Tab in a logical order; visible focus ring; no keyboard trap.
- **Colour contrast:** text vs background meets AA (4.5:1 normal, 3:1
  large), using the `src/styles/tokens.css` palette.
- **Labels and alt text:** every input has an associated label; every
  meaningful image has descriptive alt; decorative images are hidden.
- **Reduced motion:** animations respect `prefers-reduced-motion`.

## Run commands

```
# Full a11y smoke across the five routes (needs a preview/dev server)
npm run test:a11y

# A single named spec while debugging
npx playwright test tests/a11y/smoke.spec.ts -g "name of test"
```

`npm run test:a11y` exists after Phase 1 scaffolds `package.json`. The
run needs a server: build then `npm run preview`, or `npm run dev`.

## Pass criteria

| Severity   | Rule                                                |
| ---------- | --------------------------------------------------- |
| Critical   | Block. Must fix before merge. Fails a11y.yml.       |
| Serious    | Block. Must fix before merge. Fails a11y.yml.       |
| Moderate   | Warn. Track as backlog.                             |
| Minor      | Inform. Track only.                                 |

## Hard rules

- Never silence an axe rule to make a page pass.
- Never `eslint-disable` a `jsx-a11y` rule in a component to dodge a
  finding.
- Always run against the design-token colours, not ad-hoc hex values.
