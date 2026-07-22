import { defineConfig } from "vitest/config";

// Deux familles de tests :
//  - LOGIQUE des primitives (store Toast…) en environnement node (.test.ts) ;
//  - RENDU des composants React en jsdom via Testing Library (.test.tsx),
//    chaque fichier déclarant `// @vitest-environment jsdom` en tête.
// Les E2E Playwright (axe inclus, apps/web) restent la couverture d'intégration.
export default defineConfig({
  esbuild: { jsx: "automatic" },
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
  },
});
