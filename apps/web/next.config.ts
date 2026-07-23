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
  // Packages workspace en TS source -> transpilés par Next.
  transpilePackages: ["@irminsul/ui", "@irminsul/data-access"],
  // Prisma reste externe au bundle serveur (moteur natif, jamais côté client).
  serverExternalPackages: ["@prisma/client", ".prisma/client"],
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
