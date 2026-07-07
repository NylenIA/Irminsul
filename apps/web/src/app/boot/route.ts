import { NextResponse, type NextRequest } from "next/server";

/**
 * Amorçage desktop : Tauri navigue ici UNE fois par lancement avec le nonce généré.
 * Si valide → cookie httpOnly SameSite=Strict (inaccessible au JS et aux pages externes)
 * puis redirection vers le dashboard. Le nonce n'est jamais journalisé ni persisté.
 * NB : Next standalone en production ne journalise pas les URLs de requêtes ; la présence
 * du nonce en query est éphémère (mémoire process) — limite documentée dans le middleware.
 */
export function GET(request: NextRequest): NextResponse {
  const expected = process.env["IRMINSUL_NONCE"];
  if (!expected) {
    // Mode web : /boot n'a pas de rôle — retour au dashboard.
    return NextResponse.redirect(new URL("/", request.url));
  }
  const presented = request.nextUrl.searchParams.get("n");
  if (presented !== expected) {
    return new NextResponse("Forbidden (boot)", { status: 403 });
  }
  const res = NextResponse.redirect(new URL("/", request.url));
  res.cookies.set("irm_nonce", expected, {
    httpOnly: true,
    sameSite: "strict",
    secure: false, // loopback HTTP local
    path: "/",
  });
  return res;
}
