# Integre la PR communautaire #2374 (Iansan) dans un checkout gcsim ACTUEL.
# - Extrait les fichiers du personnage (tous nouveaux) depuis le diff de la PR.
# - Enregistre le perso dans les fichiers *.dm.go au format d'aujourd'hui
#   (la PR date d'un an : ses fichiers d'enregistrement ont ete deplaces).
# Idempotent ; sort en erreur si quelque chose cloche (la CI a un repli).
# Usage : python patch_gcsim_iansan.py <gcsim_dir> <pr_diff_file>
import re
import sys
from pathlib import Path

CHAR = "iansan"
PRETTY = "Iansan"


def extract_new_files(patch_text: str, prefix: str) -> dict[str, str]:
    """Reconstruit les nouveaux fichiers `prefix/*` depuis un diff unifie."""
    out: dict[str, str] = {}
    blocks = re.split(r"\ndiff --git ", "\n" + patch_text)
    for b in blocks:
        m = re.match(r"a/(\S+) b/(\S+)", b)
        if not m or not m.group(2).startswith(prefix):
            continue
        if "new file mode" not in b:
            continue
        lines: list[str] = []
        in_hunk = False
        for line in b.split("\n"):
            if line.startswith("@@"):
                in_hunk = True
                continue
            if in_hunk:
                if line.startswith("+"):
                    lines.append(line[1:])
                elif line.startswith("\\"):  # \ No newline at end of file
                    continue
                elif line.startswith(("-", " ")):
                    continue
                else:
                    in_hunk = False
        out[m.group(2)] = "\n".join(lines) + "\n"
    return out


def modernize(content: str) -> str:
    """Adapte le code d'il y a un an aux API actuelles de gcsim.

    Constaté en CI : seuls deux packages ont été SUPPRIMÉS depuis la PR —
    `pkg/core/geometry` et `pkg/core/targets`, fusionnés dans `pkg/core/info`
    (geometry.Point -> info.Point, targets.TargettableEnemy ->
    info.TargettableEnemy). Réécriture + dédoublonnage d'imports.
    """
    content = content.replace(
        '"github.com/genshinsim/gcsim/pkg/core/geometry"',
        '"github.com/genshinsim/gcsim/pkg/core/info"',
    ).replace(
        '"github.com/genshinsim/gcsim/pkg/core/targets"',
        '"github.com/genshinsim/gcsim/pkg/core/info"',
    )
    content = re.sub(r"\bgeometry\.", "info.", content)
    content = re.sub(r"\btargets\.", "info.", content)

    # event.Hook : func(args ...interface{}) bool -> func(args ...any)
    # (les `return true/false` NUS n'existent que dans ces hooks — vérifié
    # occurrence par occurrence sur les fichiers de la PR)
    content = content.replace(
        "(args ...interface{}) bool {", "(args ...any) {")
    content = re.sub(r"^(\s*)return (?:true|false)$", r"\1return",
                     content, flags=re.M)

    # Amount : ([]float64, bool) -> []float64 ; retours à deux valeurs aplatis
    content = content.replace("([]float64, bool)", "[]float64")
    content = re.sub(r"^(\s*return .+?), (?:true|false)$", r"\1",
                     content, flags=re.M)

    # types déplacés combat -> info (mapping vérifié symbole par symbole :
    # AttackInfo/AttackCB/AttackEvent/Target -> info ; les constructeurs de
    # hitbox NewCircleHit/NewBoxHitOnTarget/... restent dans combat)
    for old, new in [("combat.AttackCB", "info.AttackCB"),
                     ("*combat.AttackEvent", "*info.AttackEvent"),
                     ("combat.Target)", "info.Target)"),
                     ("combat.AttackInfo", "info.AttackInfo")]:
        content = content.replace(old, new)

    # c.Index est devenu une méthode (champ -> func() int)
    content = re.sub(r"\bc\.Index\b(?!\()", "c.Index()", content)

    # retire l'import combat s'il n'est plus utilisé après réécriture
    if '"github.com/genshinsim/gcsim/pkg/core/combat"' in content and \
            not re.search(r"\bcombat\.", content):
        content = re.sub(
            r'^\t"github\.com/genshinsim/gcsim/pkg/core/combat"\n',
            "", content, flags=re.M)

    # garantit l'import de pkg/core/info si `info.` est utilisé
    if re.search(r"\binfo\.", content) and \
            '"github.com/genshinsim/gcsim/pkg/core/info"' not in content:
        content = content.replace(
            "import (",
            'import (\n\t"github.com/genshinsim/gcsim/pkg/core/info"',
            1,
        )
    # dédoublonne les lignes d'import identiques (bloc import multi-lignes)
    lines = content.split("\n")
    seen_imports: set[str] = set()
    out_lines: list[str] = []
    in_block = False
    for line in lines:
        if line.startswith("import ("):
            in_block = True
            seen_imports.clear()
        elif in_block and line.startswith(")"):
            in_block = False
        if in_block and line.strip().startswith('"') and line.strip() in seen_imports:
            continue
        if in_block and line.strip().startswith('"'):
            seen_imports.add(line.strip())
        out_lines.append(line)
    return "\n".join(out_lines)


def insert_sorted_triple(keys_file: Path) -> None:
    """Insere Iansan dans les 3 listes ALIGNEES de character.dm.go.

    L'alignement const/index est preserve : on insere a la meme position
    alphabetique dans chaque liste.
    """
    text = keys_file.read_text(encoding="utf-8")
    if f'"{CHAR}"' in text:
        print("keys: deja present")
        return
    # 1) liste des noms -> position alphabetique + nom d'ancre
    names = re.findall(r'^\t"([a-z0-9]+)",$', text, re.M)
    anchor = next((n for n in names if n > CHAR), None)
    if anchor is None:
        raise SystemExit("keys: ancre introuvable")
    # identifiant Go de l'ancre depuis la liste des const (commentaire // nom)
    m = re.search(rf"^\t(\w+)\s+// {anchor}$", text, re.M)
    if not m:
        raise SystemExit(f"keys: const de l'ancre {anchor} introuvable")
    anchor_ident = m.group(1)
    # 2) const : avant la ligne de l'ancre
    text = re.sub(
        rf"(^\t{anchor_ident}\s+// {anchor}$)",
        f"\t{PRETTY}                        // {CHAR}\n\\1",
        text, count=1, flags=re.M,
    )
    # 3) noms : avant "anchor",
    text = re.sub(
        rf'(^\t"{anchor}",$)', f'\t"{CHAR}",\n\\1', text, count=1, flags=re.M)
    # 4) slice de cles : avant Anchor,
    text = re.sub(
        rf"(^\t{anchor_ident},$)", f"\t{PRETTY},\n\\1", text, count=1,
        flags=re.M,
    )
    keys_file.write_text(text, encoding="utf-8")
    print(f"keys: insere avant {anchor}")


def append_map_entry(path: Path, entry: str, guard: str) -> None:
    text = path.read_text(encoding="utf-8")
    if guard in text:
        print(f"{path.name}: deja present")
        return
    # insere avant la derniere accolade fermante du fichier
    idx = text.rstrip().rfind("}")
    if idx < 0:
        raise SystemExit(f"{path.name}: pas d'accolade finale")
    text = text[:idx] + entry + "\n" + text[idx:]
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}: entree ajoutee")


def main() -> None:
    gcsim = Path(sys.argv[1])
    patch_text = Path(sys.argv[2]).read_text(encoding="utf-8",
                                             errors="replace")

    # 1) fichiers du personnage
    files = extract_new_files(patch_text, f"internal/characters/{CHAR}/")
    if len(files) < 8:
        raise SystemExit(f"extraction suspecte : {len(files)} fichiers")
    for rel, content in files.items():
        dest = gcsim / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".go"):
            content = modernize(content)
        dest.write_text(content, encoding="utf-8")
    print(f"{len(files)} fichiers du perso ecrits (API modernisees)")

    # 2) enregistrements (format actuel *.dm.go)
    insert_sorted_triple(gcsim / "pkg/core/keys/character.dm.go")
    append_map_entry(
        gcsim / "pkg/shortcut/character.dm.go",
        f'\t"{CHAR}":            keys.{PRETTY},',
        f'"{CHAR}"',
    )
    append_map_entry(
        gcsim / "internal/services/assets/character.dm.go",
        f'\t"{CHAR}":            "UI_AvatarIcon_{PRETTY}",',
        f'"{CHAR}"',
    )
    imports = gcsim / "pkg/simulation/imports.character.dm.go"
    text = imports.read_text(encoding="utf-8")
    if f"characters/{CHAR}" not in text:
        line = f'\t_ "github.com/genshinsim/gcsim/internal/characters/{CHAR}"'
        idx = text.rstrip().rfind(")")
        text = text[:idx] + line + "\n" + text[idx:]
        imports.write_text(text, encoding="utf-8")
        print("imports: ajoute")
    else:
        print("imports: deja present")

    print("OK - iansan integre (compilation a valider)")


if __name__ == "__main__":
    main()
