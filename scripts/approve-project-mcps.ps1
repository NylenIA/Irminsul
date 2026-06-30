# Aide a l'approbation des MCP projet (etape interactive). N'approuve rien tout seul.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot/..").Path
Write-Output "MCP projet declares dans .mcp.json :"
(Get-Content "$root/.mcp.json" -Raw | ConvertFrom-Json).mcpServers.PSObject.Properties.Name | ForEach-Object { Write-Output "  - $_" }
Write-Output ""
Write-Output "Pour lister/approuver :"
Write-Output "  claude mcp list"
Write-Output "  claude mcp get next-devtools"
Write-Output ""
Write-Output "Action interactive unique : dans un terminal Claude Code, taper /mcp puis approuver 'next-devtools'."
Write-Output "Test reel (apres approbation), avec le dev server actif (npm run dev --workspace apps/web) :"
Write-Output "  outils next-devtools : get_project_metadata, get_routes, get_errors, get_logs"
