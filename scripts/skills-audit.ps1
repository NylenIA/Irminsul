$ErrorActionPreference = "Continue"
Write-Host "Recherche de skills Genshin spécifiques"
npx skills find "genshin impact"
Write-Host "Vérification des mises à jour des skills installés"
npx skills check
Write-Host "Inspecte manuellement tout SKILL.md et script avant installation."
