import Link from "next/link";
import type { FinalCharacterStats, FinalStatCell } from "@irminsul/engine-client";
import { loadFinalStatsAction } from "./final-stats-actions";

export const dynamic = "force-dynamic";

const fmt = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const fmt1 = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 1 });

const DMG_LABELS: Record<string, string> = {
  pyro_dmg_: "Dégâts Pyro", hydro_dmg_: "Dégâts Hydro", electro_dmg_: "Dégâts Électro",
  cryo_dmg_: "Dégâts Cryo", anemo_dmg_: "Dégâts Anémo", geo_dmg_: "Dégâts Géo",
  dendro_dmg_: "Dégâts Dendro", physical_dmg_: "Dégâts Physiques", heal_: "Bonus de soin",
};

export default async function CharacterDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<React.ReactElement> {
  const { id } = await params;
  const key = decodeURIComponent(id);
  const res = await loadFinalStatsAction(key);

  return (
    <main style={{ padding: "clamp(16px, 4vw, 40px)", maxWidth: 900, margin: "0 auto", display: "grid", gap: 16 }}>
      <div>
        <Link href="/characters" className="irm-btn irm-btn--ghost" style={{ fontSize: 13 }}>
          ← Personnages
        </Link>
      </div>
      <header>
        <h1 style={{ margin: 0 }}>{key}</h1>
        <p style={{ color: "var(--irm-text-dim)", marginTop: 4, fontSize: 13 }}>
          Statistiques finales (hors écran du jeu) calculées par le moteur — aucune valeur estimée.
        </p>
      </header>

      {!res.ok ? (
        <div className="irm-state" role="status">
          <span className="irm-state__title">
            {res.kind === "empty"
              ? "Aucun scan de compte"
              : res.kind === "not_found"
                ? "Personnage introuvable dans le scan"
                : res.kind === "unsupported"
                  ? "Personnage non pris en charge par le moteur"
                  : "Erreur du moteur"}
          </span>
          <span>{res.message}</span>
        </div>
      ) : (
        <StatsView stats={res.stats} />
      )}
    </main>
  );
}

function StatsView({ stats: s }: { stats: FinalCharacterStats }): React.ReactElement {
  const confLabel = s.confidence === "high" ? "haute" : s.confidence === "medium" ? "moyenne" : "faible";
  const confClass = s.confidence === "high" ? "irm-badge--verified" : "irm-badge--warn";
  return (
    <>
      <section className="irm-card irm-halo irm-fade-in" aria-label={`Stats finales de ${s.key}`}>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginBottom: 4 }}>
          <span className={`irm-badge ${s.complete ? "irm-badge--verified" : "irm-badge--warn"}`}>
            {s.complete ? "écran du jeu reproduit" : "stats partielles"}
          </span>
          <span className={`irm-badge ${confClass}`}>confiance {confLabel}</span>
          <span className="irm-badge">contrat {s.contractVersion}</span>
          {s.level !== undefined ? <span className="irm-badge">Niv. {s.level}</span> : null}
          {s.constellation !== undefined ? <span className="irm-badge">C{s.constellation}</span> : null}
        </div>
        <p style={{ color: "var(--irm-text-faint)", fontSize: 12.5, margin: "4px 0 12px" }}>{s.note}</p>

        <table className="irm-table" aria-label="Détail des statistiques">
          <tbody>
            <StatRow label="PV" cell={s.hp} format={fmt} />
            <StatRow label="ATQ" cell={s.atk} format={fmt} />
            <StatRow label="DÉF" cell={s.def} format={fmt} />
            <StatRow label="Taux crit." cell={s.critRate} format={fmt1} suffix=" %" />
            <StatRow label="Dégâts crit." cell={s.critDamage} format={fmt1} suffix=" %" />
            <StatRow label="Maîtrise élémentaire" cell={s.elementalMastery} format={fmt} />
            <StatRow label="Recharge d'énergie" cell={s.energyRecharge} format={fmt1} suffix=" %" />
          </tbody>
        </table>

        {Object.keys(s.damageBonuses).length > 0 ? (
          <p style={{ marginTop: 10, fontSize: 12.5 }}>
            {Object.entries(s.damageBonuses).map(([k, v]) => (
              <span key={k} className="irm-badge irm-badge--gold" style={{ marginRight: 4, marginBottom: 4 }}>
                {DMG_LABELS[k] ?? k} +{fmt1.format(v)} %
              </span>
            ))}
          </p>
        ) : null}
      </section>

      <section className="irm-card irm-fade-in" aria-label="Arme">
        <h2 className="irm-card__title" style={{ fontSize: 14 }}>Arme</h2>
        {s.weapon.valid ? (
          <p style={{ color: "var(--irm-text-dim)", fontSize: 13, margin: 0 }}>
            {s.weapon.key} · ATQ de base {s.weapon.baseAtk !== null ? fmt.format(s.weapon.baseAtk!) : "?"}
            {s.weapon.secondaryStatKey
              ? ` · stat secondaire ${s.weapon.secondaryStatKey} ${s.weapon.secondaryStatValue !== null ? fmt1.format(s.weapon.secondaryStatValue!) : "?"}`
              : ""}
          </p>
        ) : (
          <p style={{ color: "var(--irm-text-faint)", fontSize: 13, margin: 0 }}>
            {s.weapon.key ?? "Arme"} — non prise en charge par le moteur (ATQ/stat secondaire non incluses, jamais estimées).
          </p>
        )}
      </section>

      {s.warnings.length > 0 ? (
        <section className="irm-card irm-fade-in" role="status" aria-label="Données manquantes">
          <h2 className="irm-card__title" style={{ fontSize: 14 }}>
            <span className="irm-badge irm-badge--warn" style={{ marginRight: 6 }}>données manquantes</span>
          </h2>
          <ul style={{ margin: "6px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
            {s.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </section>
      ) : null}

      <details className="irm-card irm-fade-in">
        <summary style={{ cursor: "pointer", color: "var(--irm-cyan)", fontSize: 13 }}>
          Hypothèses & provenance
        </summary>
        <ul style={{ margin: "8px 0 0", paddingLeft: 18, color: "var(--irm-text-dim)", fontSize: 13 }}>
          {s.assumptions.map((a) => (
            <li key={a}>{a}</li>
          ))}
          <li>
            Source : {s.provenance.source ?? "scan local"}
            {s.provenance.snapshotDate ? ` · importé le ${s.provenance.snapshotDate}` : ""}
            {s.provenance.goodVersion ? ` · GOOD v${s.provenance.goodVersion}` : ""}.
          </li>
        </ul>
      </details>
    </>
  );
}

function StatRow({
  label,
  cell,
  format,
  suffix = "",
}: {
  label: string;
  cell: FinalStatCell;
  format: Intl.NumberFormat;
  suffix?: string;
}): React.ReactElement {
  return (
    <tr>
      <th scope="row" style={{ textAlign: "left", fontWeight: 500, color: "var(--irm-text-dim)", padding: "4px 12px 4px 0" }}>
        {label}
      </th>
      <td style={{ fontFamily: "var(--irm-mono)", padding: "4px 0" }}>
        {cell.value !== null ? `${format.format(cell.value)}${suffix}` : "—"}
        {!cell.complete ? (
          <span className="irm-badge irm-badge--warn" style={{ marginLeft: 8, fontSize: 10 }} title={cell.missing.join(" ; ")}>
            partiel
          </span>
        ) : null}
      </td>
    </tr>
  );
}
