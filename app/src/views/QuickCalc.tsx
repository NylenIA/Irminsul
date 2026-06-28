/** Calcul rapide déterministe (Phase 3) : l'utilisateur saisit ses stats, le moteur
 * renvoie le résultat + le détail (« Voir le calcul ») avec traçabilité du registre.
 * Aucune donnée de jeu factice : les champs sont des entrées éditables. */
import { useEffect, useState } from "react";
import {
  getCharacters,
  getCharacterStats,
  isDesktop,
  quickCalc,
  type CharacterInfo,
  type QuickCalcResult,
} from "../engine";

interface Fields {
  scaling: string;
  stat: string;
  crit_rate: string;
  crit_damage: string;
  damage_bonus: string;
  resistance: string;
  reaction: string;
  em: string;
}

const DEFAULTS: Fields = {
  scaling: "2.0", stat: "2000", crit_rate: "0.5", crit_damage: "1.0",
  damage_bonus: "0.0", resistance: "0.1", reaction: "", em: "0",
};

const REACTION_GROUPS: ReadonlyArray<{ label: string; items: string[] }> = [
  { label: "Amplifiantes", items: ["forward-vaporize", "reverse-vaporize", "forward-melt", "reverse-melt"] },
  { label: "Additives", items: ["aggravate", "spread"] },
  {
    label: "Transformatrices",
    items: ["overloaded", "superconduct", "electro-charged", "swirl", "bloom",
      "hyperbloom", "burgeon", "burning", "shattered"],
  },
];

export function QuickCalc(): JSX.Element {
  const [f, setF] = useState<Fields>(DEFAULTS);
  const [res, setRes] = useState<QuickCalcResult | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [characters, setCharacters] = useState<string[]>([]);
  const [selected, setSelected] = useState("");
  const [charInfo, setCharInfo] = useState<CharacterInfo | null>(null);

  function set<K extends keyof Fields>(k: K, v: string): void {
    setF((p) => ({ ...p, [k]: v }));
  }

  useEffect(() => {
    if (!isDesktop()) return;
    void getCharacters()
      .then((r) => {
        if (r.status === "ok") setCharacters(r.characters);
      })
      .catch(() => undefined);
  }, []);

  async function selectCharacter(key: string): Promise<void> {
    setSelected(key);
    setCharInfo(null);
    if (!key) return;
    try {
      const r = await getCharacterStats(key);
      if (r.status === "ok") {
        setCharInfo(r.character);
        const t = r.character.artifact_stats.totals;
        // Préremplissage HONNÊTE : artéfacts uniquement (+ base crit fixe), hors arme/ascension.
        const cr = ((t.critRate_ ?? 0) + 5) / 100;
        const cd = ((t.critDMG_ ?? 0) + 50) / 100;
        const em = t.eleMas ?? 0;
        setF((p) => ({
          ...p,
          crit_rate: cr.toFixed(3),
          crit_damage: cd.toFixed(3),
          em: String(Math.round(em)),
        }));
      } else if (r.status === "not_found") {
        setErr(`Personnage introuvable : ${r.key}`);
      }
    } catch (e) {
      setErr(String(e));
    }
  }

  async function compute(): Promise<void> {
    if (!isDesktop()) {
      setErr("Le calcul s'exécute dans l'application desktop (moteur local).");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const params: Record<string, number | string> = {
        scaling: Number(f.scaling),
        stat: Number(f.stat),
        crit_rate: Number(f.crit_rate),
        crit_damage: Number(f.crit_damage),
        damage_bonus: Number(f.damage_bonus),
        resistance: Number(f.resistance),
      };
      if (f.reaction) {
        params.reaction = f.reaction;
        params.em = Number(f.em);
      }
      setRes(await quickCalc(params));
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  const field = (label: string, key: keyof Fields, step = "0.01") => (
    <label className="qc-field">
      <span>{label}</span>
      <input
        type="number"
        inputMode="decimal"
        step={step}
        value={f[key]}
        onChange={(ev) => set(key, ev.target.value)}
      />
    </label>
  );

  return (
    <div className="quickcalc">
      <p className="empty-state">
        Calcul déterministe d'un coup direct. Sélectionne un personnage importé (préremplit
        crit/EM depuis tes artéfacts) ou saisis tes stats. Détail et sources via « Voir le calcul ».
      </p>

      {characters.length > 0 && (
        <div className="char-pick">
          <label className="qc-field">
            <span>Personnage (importé du compte)</span>
            <select value={selected} onChange={(ev) => void selectCharacter(ev.target.value)}>
              <option value="">— choisir —</option>
              {characters.map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
          </label>
          {charInfo && (
            <div className="char-info">
              <p>
                C{charInfo.constellation ?? "?"} · niv {charInfo.level ?? "?"} · talents{" "}
                {charInfo.talents.auto ?? "?"}/{charInfo.talents.skill ?? "?"}/{charInfo.talents.burst ?? "?"} ·{" "}
                {charInfo.weapon ? `${charInfo.weapon.key} R${charInfo.weapon.refinement ?? "?"}` : "sans arme"}
              </p>
              <p className="qc-prov">
                Crit/EM préremplis depuis les artéfacts (hors base/arme/ascension). Provenance :{" "}
                {charInfo.provenance.source ?? "—"} · snapshot {charInfo.provenance.snapshot_date ?? "—"}.
              </p>
              <details>
                <summary>Non pris en charge (ne pas considérer comme actif)</summary>
                <ul className="qc-mechanics">
                  {charInfo.unsupported.map((u) => (
                    <li key={u.item}><strong>{u.item}</strong> — {u.reason}</li>
                  ))}
                  {charInfo.artifact_stats.uncomputed_main.map((m, i) => (
                    <li key={`uc-${i}`}>
                      stat principale {m.mainStatKey} ({m.set} {m.slot}, {m.rarity}★ niv{m.level}) — {m.reason}
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          )}
        </div>
      )}

      <form
        className="qc-grid"
        onSubmit={(ev) => {
          ev.preventDefault();
          void compute();
        }}
      >
        {field("Multiplicateur talent (ex. 2.0)", "scaling")}
        {field("ATQ finale (depuis le jeu — base non calculée)", "stat", "1")}
        {field("Taux crit (0–1)", "crit_rate")}
        {field("Dégâts crit (ex. 1.0)", "crit_damage")}
        {field("Bonus de dégâts (0–…)", "damage_bonus")}
        {field("RES ennemie (ex. 0.1)", "resistance")}
        <label className="qc-field">
          <span>Réaction</span>
          <select value={f.reaction} onChange={(ev) => set("reaction", ev.target.value)}>
            <option value="">aucune</option>
            {REACTION_GROUPS.map((g) => (
              <optgroup key={g.label} label={g.label}>
                {g.items.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>
        {f.reaction ? field("Maîtrise élémentaire", "em", "1") : null}
        <button type="submit" disabled={busy}>{busy ? "Calcul…" : "Calculer"}</button>
      </form>

      {err && <p className="error" role="alert">{err}</p>}

      {res && (
        <div className="qc-result">
          <p>
            <strong>Dégâts finaux (moyenne) :</strong> {Math.round(res.result.expected).toLocaleString("fr-FR")} ·{" "}
            non-crit {Math.round(res.result.non_crit).toLocaleString("fr-FR")} ·{" "}
            crit {Math.round(res.result.crit).toLocaleString("fr-FR")}
          </p>
          {res.additive && (
            <p className="warn">
              Bonus additif (intégré à la base) : +{Math.round(res.additive.base_bonus_damage).toLocaleString("fr-FR")}
            </p>
          )}
          {res.transformative && (
            <p className="warn">
              Réaction transformatrice : {Math.round(res.transformative.damage).toLocaleString("fr-FR")} dégâts
              {" "}(instance séparée, sans crit)
            </p>
          )}
          <button type="button" className="link" onClick={() => setShow((s) => !s)}>
            {show ? "Masquer le calcul" : "Voir le calcul"}
          </button>
          {show && (
            <div className="qc-detail-wrap">
              <dl className="qc-detail">
                <dt>Base (stat × multiplicateur + additif)</dt><dd>{Math.round(res.result.raw_base).toLocaleString("fr-FR")}</dd>
                <dt>Multiplicateur DEF</dt><dd>{res.result.defense_multiplier.toFixed(4)}</dd>
                <dt>Multiplicateur RES</dt><dd>{res.result.resistance_multiplier.toFixed(4)}</dd>
                <dt>Multiplicateur crit attendu</dt><dd>{res.result.expected_crit_multiplier.toFixed(4)}</dd>
                {res.amplifying && (
                  <>
                    <dt>Réaction amplifiante</dt>
                    <dd>×{res.amplifying.amplifying_multiplier.toFixed(3)} (bonus EM {res.amplifying.em_bonus.toFixed(3)})</dd>
                  </>
                )}
                {res.additive && (
                  <>
                    <dt>Réaction additive</dt>
                    <dd>coef {res.additive.base_multiplier} · bonus EM {res.additive.em_bonus.toFixed(3)}</dd>
                  </>
                )}
                {res.transformative && (
                  <>
                    <dt>Réaction transformatrice</dt>
                    <dd>{res.transformative.reaction} · coef {res.transformative.base_multiplier} · bonus EM {res.transformative.em_bonus.toFixed(3)}</dd>
                  </>
                )}
              </dl>
              {charInfo && (
                <p className="qc-prov">
                  Données du compte utilisées : {charInfo.key} (C{charInfo.constellation ?? "?"}, niv{" "}
                  {charInfo.level ?? "?"}) — crit/EM issus des artéfacts ; SHA{" "}
                  {charInfo.provenance.sha256 ? `${charInfo.provenance.sha256.slice(0, 8)}…` : "—"}.
                </p>
              )}
              <p className="qc-prov">Registre v{res.registry_version} — mécaniques, sources et confiance :</p>
              <ul className="qc-mechanics">
                {res.mechanics_detail.map((m) => (
                  <li key={m.id}>
                    <strong>{m.id}</strong> — statut {m.status}, confiance {m.confidence}
                    {m.sources.length > 0
                      ? ` · ${m.sources.map((s) => `${s.name} (rang ${s.type})`).join(", ")}`
                      : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
