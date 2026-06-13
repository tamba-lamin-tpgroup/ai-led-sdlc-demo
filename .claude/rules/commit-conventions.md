---
description: Commit message conventions. Applies to every commit in the repository.
---

# Rule: commit conventions

## Format

```
<type>: <imperative summary, max 72 chars>

<wrapped body, lines max 72 chars, optional>

<trailers>
```

## Types

- `feat:`     a new user-visible capability
- `fix:`      a bug fix
- `chore:`    maintenance with no user-visible behaviour change
- `docs:`     documentation-only
- `test:`     test-only
- `refactor:` internal restructuring with no behaviour change
- `perf:`     performance improvement
- `build:`    build / dependency / tooling change
- `ci:`       CI configuration

## Trailers

Required on every commit (one of the traceability trailers):
- `Requirement: <ref>` - references a SPEC phase/section or a durable
  requirement id. Examples:
  `Requirement: SPEC Phase 3 - accessibility`,
  `Requirement: SPEC section 6.1 - Attraction type`,
  `Requirement: STORY-0042-tour-booking`.
- `Phase: <n>` - shorthand for SPEC.md phase n.
- `Incident: <id>` - hotfix only.

Enforced by `/code-push` and the `pre-tool-bash` hook.

Issue linkage (when an issue exists):
- `Refs: #<num>` for in-progress work, OR
- `Closes: #<num>` only on the commit that finishes the issue

Forbidden:
- `Co-Authored-By: Claude ...` or any AI signature
- Emoji or icons anywhere in the message

## Examples

```
feat: add attractions repository with file-based implementation

Defines the AttractionRepository interface and the file-backed
implementation that reads src/data/attractions.json. The barrel in
src/lib/content/index.ts selects it when VITE_ATTRACTIONS_SOURCE=file.

Requirement: SPEC section 5.2 - file-based repository
Refs: #12
```

```
fix: move hard-coded "Schedule a Tour" label into content layer

The CTA string was inlined in TourCard.tsx, violating the three-layer
rule. Moved to src/content/strings.en.json and read via t().

Requirement: SPEC section 5 - three-layer separation
Closes: #31
```

```
feat: enable RLS on saved_attractions with auth.uid policy

Phase: 5
Refs: #40
```
