/** Calcul rapide déterministe (Phase 3) : l'utilisateur saisit ses stats, le moteur
 * renvoie le résultat + le détail (« Voir le calcul ») avec traçabilité du registre.
 * Aucune donnée de jeu factice : les champs sont des entrées éditables. */
import { useState } from "react";
import { isDesktop, quickCalc, type QuickCalcResult } from "../engine";

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

const REACTIONS = ["", "forward-vaporize", "reverse-vaporize", "forward-melt", "reverse-melt"];

export function QuickCalc(): JSX.Element {
  const [f, setF] = useState<Fields>(DEFAULTS);
  const [res, setRes] = useState<QuickCalcResult | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);

  function set<K extends keyof Fields>(k: K, v: string): void {
    setF((p) => ({ ...p, [k]: v }));
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
        Calcul déterministe d'un coup direct. Saisis tes stats réelles ; le détail et les
        sources sont affichés via « Voir le calcul ».
      </p>
      <form
        className="qc-grid"
        onSubmit={(ev) => {
          ev.preventDefault();
          void compute();
        }}
      >
        {field("Multiplicateur talent (ex. 2.0)", "scaling")}
        {field("Stat (ATK/HP/DEF)", "stat", "1")}
        {field("Taux crit (0–1)", "crit_rate")}
        {field("Dégâts crit (ex. 1.0)", "crit_damage")}
        {field("Bonus de dégâts (0–…)", "damage_bonus")}
        {field("RES ennemie (ex. 0.1)", "resistance")}
        <label className="qc-field">
          <span>Réaction</span>
          <select value={f.reaction} onChange={(ev) => set("reaction", ev.target.value)}>
            {REACTIONS.map((r) => (
              <option key={r || "none"} value={r}>{r || "aucune"}</option>
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
            <strong>Attendu (moyenne) :</strong> {Math.round(res.result.expected).toLocaleString("fr-FR")} ·{" "}
            non-crit {Math.round(res.result.non_crit).toLocaleString("fr-FR")} ·{" "}
            crit {Math.round(res.result.crit).toLocaleString("fr-FR")}
          </p>
          <button type="button" className="link" onClick={() => setShow((s) => !s)}>
            {show ? "Masquer le calcul" : "Voir le calcul"}
          </button>
          {show && (
            <dl className="qc-detail">
              <dt>Multiplicateur DEF</dt><dd>{res.result.defense_multiplier.toFixed(4)}</dd>
              <dt>Multiplicateur RES</dt><dd>{res.result.resistance_multiplier.toFixed(4)}</dd>
              <dt>Multiplicateur crit attendu</dt><dd>{res.result.expected_crit_multiplier.toFixed(4)}</dd>
              {res.amplifying && (
                <>
                  <dt>Réaction (amplifiante)</dt>
                  <dd>×{res.amplifying.amplifying_multiplier.toFixed(3)} (bonus EM {res.amplifying.em_bonus.toFixed(3)})</dd>
                </>
              )}
              <dt>Mécaniques utilisées</dt><dd>{res.mechanics_used.join(", ")}</dd>
              <dt>Registre</dt><dd>v{res.registry_version} (sources KQM, statut vérifié)</dd>
            </dl>
          )}
        </div>
      )}
    </div>
  );
}
