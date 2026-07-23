/**
 * Hook de démarrage Next (`register()`) — exécuté UNE fois au boot du serveur, en
 * dev comme en build standalone desktop (output: "standalone" l'embarque).
 *
 * Applique les migrations de schéma en attente à la base LOCALE via un runner
 * idempotent et transactionnel. Couvre le cas d'une MAJ desktop d'une base
 * %APPDATA% existante (le CLI Prisma n'est pas embarqué). Sur une base déjà à jour
 * (cas courant) c'est un strict no-op.
 *
 * Non bloquant par conception : toute erreur est journalisée sans être propagée —
 * le serveur démarre quand même et le Diagnostic signalera une dérive résiduelle
 * (checkSchemaDrift) plutôt qu'un crash au boot.
 */
export async function register(): Promise<void> {
  // Prisma (Node) n'existe pas sur le runtime edge : ne s'exécute que côté nodejs.
  if (process.env["NEXT_RUNTIME"] !== "nodejs") return;
  try {
    const { prisma, applyPendingMigrations } = await import("@irminsul/data-access");
    const result = await applyPendingMigrations(prisma);
    if (result.status === "applied") {
      console.info(`[irminsul] migrations appliquées au démarrage : ${result.applied.join(", ")}`);
    }
  } catch (error) {
    console.error(
      `[irminsul] migration au démarrage échouée (non bloquant) : ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}
