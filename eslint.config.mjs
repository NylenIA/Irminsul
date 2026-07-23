import tseslint from "typescript-eslint";
import nextPlugin from "@next/eslint-plugin-next";

/**
 * Lint TypeScript + scripts du monorepo (typescript-eslint recommended, flat config).
 * Périmètre : tout le TS/TSX applicatif (apps/web + packages) ET les scripts
 * d'outillage `scripts/*.mjs` (globals Node déclarés explicitement, sans dépendance
 * supplémentaire). Le code généré/vendored et `app/**` (Tauri) restent exclus.
 * Les règles Next-spécifiques (eslint-config-next) pourront s'ajouter plus tard.
 * Câblé dans `npm run verify` via `lint:web`.
 */
export default tseslint.config(
  {
    ignores: [
      "**/node_modules/**",
      "**/.next/**",
      "**/dist/**",
      "**/build/**",
      "app/**",
      "**/.e2e/**",
      "**/playwright-report/**",
      "**/test-results/**",
      ".irminsul/**",
      "data/**",
      "tools/**",
      "simulations/**",
      "**/*.js",
    ],
  },
  ...tseslint.configs.recommended,
  {
    // Règles Next-spécifiques (pièges app-router, images, Core Web Vitals),
    // scopées sur l'app Next uniquement. Preset flat officiel du plugin.
    ...nextPlugin.configs["core-web-vitals"],
    files: ["apps/web/**/*.{ts,tsx}"],
  },
  {
    // Scripts Node (.mjs) : globals du runtime déclarés explicitement (pas de
    // dépendance `globals`) pour que no-undef reste utile sans faux positifs.
    files: ["scripts/**/*.mjs", "eslint.config.mjs"],
    languageOptions: {
      globals: {
        console: "readonly",
        process: "readonly",
        URL: "readonly",
        fetch: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        Buffer: "readonly",
        TextDecoder: "readonly",
        AbortController: "readonly",
      },
    },
  },
  {
    rules: {
      // Convention : préfixe `_` = volontairement inutilisé (args de contrat, destructuring).
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_", caughtErrorsIgnorePattern: "^_" },
      ],
    },
  },
);
