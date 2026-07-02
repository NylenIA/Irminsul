# SidecarEngineClient — le vrai moteur Python derrière le contrat

## Chaîne
`Team Lab → Server Action (previewDirectHitAction) → [IRMINSUL_ENGINE=sidecar ?]
→ SidecarEngineClient → scripts/engine_stdio.py (process one-shot) → irminsul.damage/reaction`
Repli : `LocalEngineClient` (port TS, parité goldens) — **`provenance.engine` reflète toujours
le moteur réellement utilisé** (`python-sidecar` vs `ts-port`), jamais de faux étiquetage.

## Protocole (borné)
stdin : `{"method": calculate_direct_hit|amplifying_multiplier|transformative_reaction, "params":{...}}`
stdout : `{"ok":true,"result":{...},"engine":"python-sidecar"}` ou `{"ok":false,"error":"..."}`.
Entrée max 64 Ko ; une requête = un process = exit.

## Sécurité (exigences mission)
`shell:false` · `windowsHide:true` (aucune console visible) · timeout + kill (8 s Server
Action, 10 s défaut) · stderr borné (2 Ko) · JSON strict sinon `SidecarError` typée · aucun
secret en argument · aucun processus orphelin (one-shot + kill au timeout).

## Configuration
`IRMINSUL_ENGINE=sidecar` (sinon moteur TS local) · `IRMINSUL_PYTHON` (défaut :
`.venv/Scripts/python.exe` du dépôt). Machine de dev uniquement — la distribution desktop
utilise le sidecar PyInstaller de Tauri (autre canal, déjà livré phase 2).

## Tests
Parité **à travers le pont** (sidecar == local à 1e-9, provenance `python-sidecar`) ·
méthode inconnue → `SidecarError` · python introuvable → `SidecarError` (repli local par
l'appelant). Skip propre si le venv est absent (CI sans Python).
