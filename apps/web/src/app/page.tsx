import Link from "next/link";
import { getTeamRepository } from "@irminsul/data-access";
import { loadAccountSummary } from "@/server/account";

export const dynamic = "force-dynamic";

/**
 * Accueil = parcours GUIDÉ en 3 étapes, avec l'état réel de chacune (aucun
 * chiffre décoratif). Le jargon technique (contrats moteur, goldens…) vit au
 * Diagnostic — pas ici : ici on répond à « je fais quoi, maintenant ? ».
 */
export default async function HomePage(): Promise<React.ReactElement> {
  const account = await loadAccountSummary();
  let teamsCount: number | null = null;
  try {
    teamsCount = (await getTeamRepository().list()).length;
  } catch {
    teamsCount = null;
  }
  const hasAccount = account !== null && account.characters.length > 0;
  const hasTeams = (teamsCount ?? 0) > 0;

  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 900, margin: "0 auto", display: "grid", gap: 20 }}>
      <header>
        <h1 style={{ margin: 0 }}>Irminsul</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 14 }}>
          Ton assistant Genshin, en local : importe ton compte, vois tes personnages,
          construis et compare tes équipes. Tes données ne quittent jamais ta machine.
        </p>
      </header>

      <section aria-label="Parcours" style={{ display: "grid", gap: 12 }}>
        <StepCard
          n={1}
          done={hasAccount}
          href="/characters"
          title="Importe ton compte"
          doneLabel={
            hasAccount
              ? `${account.characters.length} personnages importés${account.importedAt ? ` (scan du ${account.importedAt})` : ""}`
              : null
          }
          todoLabel="Choisis ton fichier de scan (.json d'InventoryKamera) — 30 secondes, aucun outil à installer."
          cta={hasAccount ? "Mettre à jour le scan" : "Importer maintenant"}
        />
        <StepCard
          n={2}
          done={hasAccount}
          href="/characters"
          title="Regarde tes personnages"
          doneLabel={hasAccount ? "Builds réels : niveau, armes, artéfacts, stats finales calculées." : null}
          todoLabel="Dès l'import fait, chaque personnage affiche son vrai build et ses stats finales."
          cta="Voir mes personnages"
        />
        <StepCard
          n={3}
          done={hasTeams}
          href="/team-lab"
          title="Construis tes équipes"
          doneLabel={hasTeams ? `${teamsCount} équipe${(teamsCount ?? 0) > 1 ? "s" : ""} sauvegardée${(teamsCount ?? 0) > 1 ? "s" : ""} — compare-les, teste des dégâts.` : null}
          todoLabel="Compose une équipe depuis ton roster, sauvegarde-la, et vois ce qu'elle vaut."
          cta={hasTeams ? "Ouvrir mes équipes" : "Créer ma première équipe"}
        />
      </section>

      <section className="irm-card" aria-label="Pour aller plus loin">
        <h2 className="irm-card__title" style={{ fontSize: 14 }}>Pour aller plus loin</h2>
        <ul style={{ margin: "6px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13, display: "grid", gap: 4 }}>
          <li><Link href="/rotations" style={{ color: "var(--irm-cyan)" }}>Dégâts d&apos;équipe</Link> — chiffre une suite d&apos;actions avec tes vrais builds.</li>
          <li><Link href="/team-compare" style={{ color: "var(--irm-cyan)" }}>Comparateur</Link> — deux équipes, une cible commune, un verdict sourcé.</li>
          <li><Link href="/recommendations" style={{ color: "var(--irm-cyan)" }}>Recommandations</Link> — améliorations classées, basées sur tes données.</li>
          <li><Link href="/simulation" style={{ color: "var(--irm-cyan)" }}>Simulation avancée</Link> — simulations complètes gcsim (pour les curieux).</li>
        </ul>
      </section>
    </main>
  );
}

function StepCard({
  n,
  done,
  href,
  title,
  doneLabel,
  todoLabel,
  cta,
}: {
  n: number;
  done: boolean;
  href: string;
  title: string;
  doneLabel: string | null;
  todoLabel: string;
  cta: string;
}): React.ReactElement {
  return (
    <article className="irm-card irm-fade-in" style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
      <span
        aria-hidden="true"
        style={{
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          width: 30, height: 30, borderRadius: "50%", flexShrink: 0, fontWeight: 600,
          background: done ? "var(--irm-success, #2f9e6e)" : "var(--irm-surface-2, #26262c)",
          color: done ? "#fff" : "var(--irm-text-dim)",
          border: done ? "none" : "1px solid var(--irm-border)",
        }}
      >
        {done ? "✓" : n}
      </span>
      <div style={{ display: "grid", gap: 4 }}>
        <h2 className="irm-card__title" style={{ fontSize: 15, margin: 0 }}>{title}</h2>
        <p style={{ margin: 0, color: "var(--irm-text-dim)", fontSize: 13 }}>
          {done && doneLabel ? doneLabel : todoLabel}
        </p>
        <Link href={href} className={`irm-btn ${done ? "irm-btn--ghost" : "irm-btn--primary"}`} style={{ justifySelf: "start", marginTop: 4 }}>
          {cta}
        </Link>
      </div>
    </article>
  );
}
