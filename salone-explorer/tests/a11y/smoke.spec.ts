// A11y smoke — WCAG 2.2 AA axe-core scan on the five required routes.
// Fails CI on serious or critical violations (SPEC §15, CLAUDE.md).
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const SMOKE_ROUTES = [
  { path: "/", name: "Home" },
  { path: "/attractions/tiwai-island", name: "Attraction detail" },
  { path: "/about", name: "About" },
  { path: "/signin", name: "Sign In" },
  { path: "/signup", name: "Sign Up" },
];

for (const route of SMOKE_ROUTES) {
  test(`${route.name} (${route.path}) — no serious/critical a11y violations`, async ({ page }) => {
    await page.goto(route.path);
    await page.waitForLoadState("networkidle");

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();

    const blocking = results.violations.filter(
      (v) => v.impact === "serious" || v.impact === "critical"
    );

    expect(blocking, `${route.name} has serious/critical violations:\n${
      blocking.map((v) => `  [${v.impact}] ${v.id}: ${v.description}`).join("\n")
    }`).toHaveLength(0);
  });
}
