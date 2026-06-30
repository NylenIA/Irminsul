# Reprise Duo apres auth Codex : verifs -> test read-only -> mission reelle de revue -> reprise produit.
# Ne fait AUCUNE integration risquee sans revue. Ne tue pas de process en masse.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path

# 1) Pre-requis
foreach ($c in @("codex","duo")) {
  if (-not (Get-Command $c -ErrorAction SilentlyContinue)) { Write-Error "$c absent"; exit 1 }
}
Write-Output ("codex " + (codex --version) + " | duo " + (duo --version))

# 2) Test read-only Codex (preuve d'auth)
codex exec --cd "$root" --sandbox read-only --ask-for-approval never --json `
  "Liste les modeles que tu peux utiliser et confirme le mode read-only." 2>&1 | Select-Object -First 5

# 3) Mission reelle a faible risque : revue read-only du TeamRepository Prisma
Write-Output "Mission Codex (read-only) : revue du TeamRepository..."
codex exec --cd "$root/packages/data-access" --sandbox read-only --ask-for-approval never --json `
  "Revue en lecture seule de src/repositories/team-repository.ts et tests/team-repository.test.ts : validation des entrees, gestion d'erreurs, transactions, tests manquants, separation serveur/client. Ne modifie aucun fichier." `
  > "$root/.duo/runtime/codex-review-team-repository.json" 2>$null
Write-Output "Revue ecrite dans .duo/runtime/ (gitignore). Claude doit la lire et trier les findings avant tout correctif."

# 4) Reprendre le produit (Team Lab)
Write-Output "Etape suivante produit : page apps/web/src/app/team-lab (cf. docs/project/NEXT_ACTIONS.md)."
