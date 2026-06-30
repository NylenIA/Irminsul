import type { NextConfig } from "next";

// En-têtes de sécurité de base (CSP affinée quand les sources réelles seront connues).
const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
];

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Packages workspace en TS source -> transpilés par Next.
  transpilePackages: ["@irminsul/ui", "@irminsul/data-access"],
  // Prisma reste externe au bundle serveur (moteur natif, jamais côté client).
  serverExternalPackages: ["@prisma/client", ".prisma/client"],
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
