---
name: Genshin Fact Checker
description: Vérifie une affirmation Genshin précise (fait, chiffre, date, nom, version) contre sources primaires/locales.
argument-hint: "<affirmation à vérifier>"
---
Fact-check : $ARGUMENTS

Applique [docs/RESEARCH_POLICY.md](../../docs/RESEARCH_POLICY.md) §1–3, §9.
1. Reformule l'affirmation en éléments vérifiables (nom, valeur, version, date).
2. Vérifie dans la base locale (`search_knowledge`, genshin-db) puis sources primaires ; recoupe.
3. Pour chaque élément : **Vrai / Faux / Partiellement vrai / Non vérifiable**, avec source + date.
4. Si non vérifiable → le dire (`safe_unknown`), ne pas inventer.
5. Donne la confiance globale et ce qui changerait le verdict.
