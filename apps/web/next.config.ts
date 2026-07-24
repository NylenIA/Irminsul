import type { NextConfig } from "next";
import path from "node:path";

// En-têtes de sécurité de base (CSP affinée quand les sources réelles seront connues).
const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
];

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  // Racine du file-tracing = racine du monorepo. Sans ça, Next remonte le disque
  // pour tracer les dépendances hoistées -> l'étape « Finalizing page optimization »
  // devient pathologiquement lente (voire bloquée) sous Windows/Defender.
  outputFileTracingRoot: path.join(process.cwd(), "..", ".."),
  // NE JAMAIS tracer/embarquer `data/` dans le bundle standalone : il contient
  // le COMPTE RÉEL du joueur (data/account, privé), la base, et data/sources
  // (genshin-db, chemins > MAX_PATH). Le tracing l'incluait -> (1) FUITE de
  // données privées dans l'installeur, (2) fichiers read-only/longs qui font
  // échouer le build Tauri (« Accès refusé »). Le moteur lit ces données au
  // runtime via le sidecar, pas via le bundle Next.
  outputFileTracingExcludes: {
    "**/*": [
      "data/**",
      "../../data/**",
      "**/data/account/**",
      "**/data/sources/**",
      "**/data/mechanics/**",
      "**/data/*.db",
    ],
  },
  // Packages workspace en TS source -> transpilés par Next.
  transpilePackages: ["@irminsul/ui", "@irminsul/data-access"],
  // Prisma reste externe au bundle serveur (moteur natif, jamais côté client).
  serverExternalPackages: ["@prisma/client", ".prisma/client"],
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
