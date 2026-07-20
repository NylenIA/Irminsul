import { defineConfig } from "vitest/config";

// Tests de la LOGIQUE des primitives (store Toast…) en environnement node —
// le rendu React est couvert par les E2E Playwright (axe inclus) côté apps/web.
export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"],
  },
});
