import tseslint from "typescript-eslint";

/**
 * Lint TypeScript du monorepo (typescript-eslint recommended, flat config).
 * Périmètre v1 : tout le TS/TSX applicatif (apps/web + packages). Les scripts
 * .mjs et le code généré/vendored sont exclus. Les règles Next-spécifiques
 * (eslint-config-next) pourront s'ajouter dans un cycle ultérieur.
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
      "scripts/**",
      "**/*.mjs",
      "**/*.js",
    ],
  },
  ...tseslint.configs.recommended,
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
