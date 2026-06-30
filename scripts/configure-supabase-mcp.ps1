# Prepare le MCP Supabase HEBERGE en read-only, scope projet. NE vise jamais la production.
# N'ecrit aucun PAT/secret en clair. Optionnel : Irminsul est local-first ; Supabase = futur.
param(
  [string]$ProjectRef = $env:SUPABASE_PROJECT_REF
)
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRef)) {
  Write-Error "SUPABASE_PROJECT_REF manquant. Fournir un projet de DEVELOPPEMENT (jamais prod) : `n  ./scripts/configure-supabase-mcp.ps1 -ProjectRef <ref>"
  exit 1
}

$url = "https://mcp.supabase.com/mcp?project_ref=$ProjectRef&read_only=true&features=database,docs"
Write-Output "Ajout d'un serveur MCP Supabase scope projet, read-only :"
Write-Output "  claude mcp add --scope project --transport http supabase `"$url`""
Write-Output ""
Write-Output "Puis :"
Write-Output "  claude mcp get supabase"
Write-Output "  claude mcp login supabase   # OAuth interactif (action utilisateur unique)"
Write-Output ""
Write-Output "Suppression propre : claude mcp remove supabase"
Write-Output "Etat tant que l'OAuth n'est pas faite : READY_FOR_USER_AUTH (pas CONNECTED)."
