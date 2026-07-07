import { NextResponse, type NextRequest } from "next/server";

/**
 * Protection nonce éphémère (desktop uniquement — audit M3).
 * Modèle de menace : un processus local tiers pourrait joindre le serveur loopback et
 * déclencher des MUTATIONS (Server Actions POST) dans la session de l'utilisateur.
 * Parade : Tauri génère un nonce par lancement (env IRMINSUL_NONCE, jamais persisté/loggé),
 * le dépose en cookie httpOnly via /boot, et TOUTE requête POST doit le présenter.
 * Les GET (rendu, assets, health check) restent libres : lecture locale non sensible.
 * Limites documentées : un processus du MÊME utilisateur pouvant lire la mémoire/env du
 * process a déjà gagné ; ce nonce bloque l'accès réseau local opportuniste, pas un malware
 * élevé. En mode web (pas d'env), le middleware est inactif.
 */
export function middleware(request: NextRequest): NextResponse {
  const expected = process.env["IRMINSUL_NONCE"];
  if (!expected) return NextResponse.next(); // web/dev : pas de nonce requis

  if (request.method === "GET" || request.method === "HEAD" || request.method === "OPTIONS") {
    return NextResponse.next();
  }
  const presented = request.cookies.get("irm_nonce")?.value;
  if (presented === expected) return NextResponse.next();
  return new NextResponse("Forbidden (nonce)", { status: 403 });
}

export const config = {
  // Tout sauf assets statiques (les mutations passent toutes par des POST applicatifs).
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
