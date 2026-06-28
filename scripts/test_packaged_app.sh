#!/usr/bin/env bash
# Valide le parcours de l'APP PACKAGÉE (pas le mode dev) en utilisant les binaires
# release produits par `tauri build`, comme le ferait l'app installée :
#   - sidecar = irminsul-sidecar.exe à côté de irminsul.exe (release dir),
#   - données dans un dossier app-data dédié (mime %APPDATA%/com.nylenia.irminsul),
#   - PATH SANS Python (preuve d'autonomie).
# Parcours : import GOOD -> profil -> roster -> RELANCE (même app-data) -> restauration.
set -uo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
REL="$ROOT/app/src-tauri/target/release"
SC="$REL/irminsul-sidecar.exe"
APP="$REL/irminsul.exe"
GOOD="${1:-$(ls data/account/raw/*.json 2>/dev/null | head -1)}"

[ -x "$SC" ] || { echo "ÉCHEC: sidecar packagé introuvable: $SC (lancer tauri build)"; exit 1; }
[ -x "$APP" ] || { echo "ÉCHEC: exe app introuvable: $APP"; exit 1; }

APPDATA_SIM="$(mktemp -d)"                       # persiste entre les 2 "sessions"
APPDATA_WIN="$(cygpath -m "$APPDATA_SIM")"
CLEANPATH="/c/Windows/System32:/c/Windows"
if [ -z "$GOOD" ] || [ ! -f "$GOOD" ]; then
  GOOD="$APPDATA_SIM/synthetic_GOOD.json"
  cat > "$GOOD" <<'JSON'
{"format":"GOOD","version":3,"source":"Inventory_Kamera",
 "characters":[{"key":"Furina","level":90,"constellation":0,"ascension":6,"talent":{"auto":1,"skill":6,"burst":6}}],
 "weapons":[{"key":"FavoniusSword","level":90,"ascension":6,"refinement":1,"location":"Furina","lock":true,"id":0}],
 "artifacts":[],"materials":{"Mora":1000}}
JSON
fi
GOODWIN="$(cygpath -m "$(realpath "$GOOD")")"

run() { printf '%s' "$1" | env -u PYTHONPATH -u PYTHONHOME PATH="$CLEANPATH" \
        IRMINSUL_PROJECT_ROOT="$APPDATA_WIN" PYTHONUTF8=1 "$SC"; }
ok() { echo "$1" | grep -q "$2" && echo "  OK: $3" || { echo "  ÉCHEC ($3): $1"; exit 1; }; }

echo "== Session 1 : import + affichage =="
ok "$(run "{\"id\":1,\"method\":\"import-good\",\"params\":{\"path\":\"$GOODWIN\"}}")" '"ok": true' "import GOOD"
ok "$(run '{"id":2,"method":"profile"}')" '"sha256"' "profil (provenance)"
ok "$(run '{"id":3,"method":"roster"}')" '"characters"' "roster (personnages/armes/sets)"
ok "$(run '{"id":31,"method":"quick-calc","params":{"scaling":2.0,"stat":2000,"crit_rate":0.5,"crit_damage":1.0,"damage_bonus":0.5}}')" '"expected"' "calcul rapide (registre embarqué)"
ok "$(run '{"id":32,"method":"characters"}')" '"characters"' "liste personnages importés"
FIRST="$(run '{"id":33,"method":"characters"}' | grep -oE '"characters": \["[^"]+' | grep -oE '[A-Za-z]+$' | head -1)"
CS="$(run "{\"id\":34,\"method\":\"character-stats\",\"params\":{\"key\":\"$FIRST\"}}")"
ok "$CS" '"artifact_stats"' "stats perso (artéfacts + provenance)"
ok "$CS" '"base_stats"' "stats de BASE perso (courbes genshin-db embarquées)"
ok "$CS" '"supported": true' "base perso calculée automatiquement (sans Python)"

echo "== Session 2 : RELANCE (même app-data, sans réimport) -> restauration =="
ok "$(run '{"id":4,"method":"profile"}')" '"status": "ok"' "profil restauré"
ok "$(run '{"id":5,"method":"roster"}')" '"characters"' "roster restauré"

echo "== app-data persistée =="
[ -f "$APPDATA_SIM/data/account/current/account-profile.json" ] && echo "  OK: données présentes sur disque" || { echo "  ÉCHEC: pas de données persistées"; exit 1; }

rm -rf "$APPDATA_SIM" 2>/dev/null || true
echo "✅ App packagée validée : import, affichage, relance et restauration — SANS Python."
