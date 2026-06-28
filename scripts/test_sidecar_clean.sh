#!/usr/bin/env bash
# Vérifie que le sidecar empaqueté fonctionne SANS Python installé.
# Lance l'exe avec un PATH minimal (sans Python) et un dossier de données temporaire,
# puis valide import GOOD -> profil -> roster (provenance conservée).
# Usage : bash scripts/test_sidecar_clean.sh [chemin_GOOD]
set -uo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
TRIPLE="${TRIPLE:-x86_64-pc-windows-msvc}"
EXE="$ROOT/app/src-tauri/binaries/irminsul-sidecar-$TRIPLE.exe"
GOOD="${1:-$(ls data/account/raw/*.json 2>/dev/null | head -1)}"

[ -x "$EXE" ] || { echo "ÉCHEC: sidecar introuvable: $EXE (lancer python tools/build_sidecar.py)"; exit 1; }

TMP="$(mktemp -d)"
TMPWIN="$(cygpath -m "$TMP")"

# Fichier GOOD : celui fourni/scanné, sinon un GOOD SYNTHÉTIQUE (CI sans données perso).
if [ -z "$GOOD" ] || [ ! -f "$GOOD" ]; then
  GOOD="$TMP/synthetic_GOOD.json"
  cat > "$GOOD" <<'JSON'
{"format":"GOOD","version":3,"source":"Inventory_Kamera",
 "characters":[{"key":"Furina","level":90,"constellation":0,"ascension":6,"talent":{"auto":1,"skill":6,"burst":6}}],
 "weapons":[{"key":"FavoniusSword","level":90,"ascension":6,"refinement":1,"location":"Furina","lock":true,"id":0}],
 "artifacts":[],"materials":{"Mora":1000}}
JSON
  echo "(GOOD synthétique utilisé)"
fi
GOODWIN="$(cygpath -m "$(realpath "$GOOD")")"  # chemin absolu (sinon résolu contre la racine temp)
# PATH minimal Windows, SANS Python (preuve d'autonomie).
CLEANPATH="/c/Windows/System32:/c/Windows"

run() { printf '%s' "$1" | env -u PYTHONPATH -u PYTHONHOME PATH="$CLEANPATH" \
        IRMINSUL_PROJECT_ROOT="$TMPWIN" PYTHONUTF8=1 "$EXE"; }

echo "== python sur le PATH nettoyé ? (doit être absent) =="
( PATH="$CLEANPATH"; command -v python >/dev/null 2>&1 && echo "python PRÉSENT (test peu probant)" || echo "python ABSENT — OK" )

echo "== import-good =="
OUT_IMP="$(run "{\"id\":\"imp\",\"method\":\"import-good\",\"params\":{\"path\":\"$GOODWIN\"}}")"
echo "$OUT_IMP" | grep -q '"ok": true' && echo "  import OK" || { echo "  ÉCHEC import: $OUT_IMP"; exit 1; }

echo "== profile (provenance) =="
OUT_PROF="$(run '{"id":"p","method":"profile"}')"
echo "$OUT_PROF" | grep -q '"sha256"' && echo "  profil+provenance OK" || { echo "  ÉCHEC profil: $OUT_PROF"; exit 1; }

echo "== roster (personnages/armes/sets) =="
OUT_ROST="$(run '{"id":"r","method":"roster"}')"
echo "$OUT_ROST" | grep -q '"characters"' && echo "  roster OK" || { echo "  ÉCHEC roster: $OUT_ROST"; exit 1; }

echo "== character-stats (stats de base perso EMBARQUÉES, sans Python) =="
OUT_CS="$(run '{"id":"cs","method":"character-stats","params":{"key":"Furina"}}')"
if echo "$OUT_CS" | grep -q '"base_stats"' && echo "$OUT_CS" | grep -q '"supported": true'; then
  echo "  stats de base sourcées OK (données genshin-db bundlées dans l'exe)"
else
  echo "  ÉCHEC base_stats (données non embarquées ?): $OUT_CS"; exit 1
fi

rm -rf "$TMP" 2>/dev/null || true
echo "✅ Sidecar autonome validé SANS Python (import + profil + roster + stats de base)."
