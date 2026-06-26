from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from .account import build_overview, import_good, load_current, render_validation_md
from .damage import calculate_direct_hit
from .enka import fetch_showcase
from .gcsim import gcsim_path, run_gcsim
from .good import inspect_good_export
from .paths import account_subdir
from .leaks import DevelopmentStage, score_leak
from .reaction import amplifying_multiplier, transformative_reaction
from .source_sync import rebuild_index, search_index, sync_repositories
from .status import system_status

# Sous Windows, Python n'active pas encore le mode UTF-8 par défaut (avant 3.15) :
# on force la sortie en UTF-8 pour que les accents et tableaux s'affichent bien
# dans cmd.exe / PowerShell sans configuration manuelle.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):  # flux déjà détaché / non reconfigurable
        pass

app = typer.Typer(help="Irminsul AI — outils Genshin pour Claude Code")
account_app = typer.Typer(help="Import et profil du compte")
damage_app = typer.Typer(help="Calculs de dégâts")
reaction_app = typer.Typer(help="Calculs de réactions élémentaires")
leak_app = typer.Typer(help="Analyse de fiabilité des leaks")
gcsim_app = typer.Typer(help="Exécution de simulations gcsim")
app.add_typer(account_app, name="account")
app.add_typer(damage_app, name="damage")
app.add_typer(reaction_app, name="reaction")
app.add_typer(leak_app, name="leak")
app.add_typer(gcsim_app, name="gcsim")
console = Console()


@app.command()
def update(index_only: bool = False) -> None:
    """Synchronise les sources et reconstruit l'index."""
    if not index_only:
        print({"sync": sync_repositories()})
    print({"index": rebuild_index()})


@app.command()
def search(query: str, limit: int = 8) -> None:
    """Recherche dans la base locale."""
    results = search_index(query, limit=limit)
    print_json(results)


@app.command()
def status() -> None:
    """Affiche la fraîcheur des données."""
    payload = system_status()
    table = Table(title="Irminsul AI status")
    table.add_column("Source")
    table.add_column("État")
    table.add_column("Commit/date")
    for source in payload["repositories"]:
        state = "active" if source["enabled"] else "désactivée"
        if source["enabled"] and not source["exists"]:
            state = "absente"
        table.add_row(source["name"], state, source.get("commit_date", source.get("commit", "—")))
    console.print(table)
    console.print(payload["index"])


@account_app.command("import-enka")
def import_enka(uid: str, force: bool = False) -> None:
    """Importe un showcase public via Enka en respectant le TTL."""
    print_json(fetch_showcase(uid, force=force))


@account_app.command("inspect-good")
def inspect_good(path: Path) -> None:
    """Inspecte un export GOOD de Genshin Optimizer."""
    print_json(inspect_good_export(path))


@account_app.command("import-good")
def import_good_cmd(
    path: Path,
    snapshot_date: str = typer.Option(None, help="Date du snapshot, défaut = aujourd'hui (YYYY-MM-DD)."),
    force: bool = typer.Option(False, help="Force la re-création du snapshot même si déjà importé."),
    write_report: bool = typer.Option(True, help="Écrit le rapport de validation markdown."),
) -> None:
    """Importe, valide, normalise et compare un export GOOD (idempotent)."""
    result = import_good(path, snapshot_date=snapshot_date, force=force)
    if write_report:
        snap_date = result["snapshot"].split("__")[0]
        report = render_validation_md(result, source_name=Path(path).name, snapshot_date=snap_date)
        report_path = account_subdir("reports") / f"import-validation-{snap_date}.md"
        report_path.write_text(report, encoding="utf-8")
        result["report"] = str(report_path)
    # On n'affiche pas tout le détail des issues pour rester lisible.
    summary = {k: v for k, v in result.items() if k not in ("diff",)}
    summary["validation"] = result["validation"]["counts_by_severity"]
    print_json(summary)


@account_app.command("summary")
def account_summary() -> None:
    """Affiche le profil normalisé courant (data/account/current)."""
    profile_path = account_subdir("current") / "account-profile.json"
    if not profile_path.exists():
        console.print("[yellow]Aucun import. Lance d'abord `irminsul account import-good <fichier>`.[/yellow]")
        raise typer.Exit(code=1)
    print_json(json.loads(profile_path.read_text(encoding="utf-8")))


@account_app.command("overview")
def account_overview() -> None:
    """Aperçu factuel (données scannées) : persos investis, drapeaux d'équipement, matériaux."""
    print_json(build_overview(load_current()))


@damage_app.command("hit")
def damage_hit(
    scaling: float = typer.Option(..., help="Multiplicateur, ex. 2.5 pour 250%"),
    stat: float = typer.Option(..., help="Stat utilisée par le talent"),
    flat: float = 0.0,
    damage_bonus: float = 0.0,
    crit_rate: float = 0.05,
    crit_damage: float = 0.50,
    attacker_level: int = 90,
    enemy_level: int = 100,
    resistance: float = 0.10,
    defense_reduction: float = 0.0,
    defense_ignore: float = 0.0,
    reaction_multiplier: float = 1.0,
    reaction_bonus: float = 0.0,
    vulnerability_multiplier: float = 1.0,
) -> None:
    result = calculate_direct_hit(
        scaling=scaling,
        scaling_stat=stat,
        flat_base_damage=flat,
        damage_bonus=damage_bonus,
        crit_rate=crit_rate,
        crit_damage=crit_damage,
        attacker_level=attacker_level,
        enemy_level=enemy_level,
        enemy_resistance=resistance,
        defense_reduction=defense_reduction,
        defense_ignore=defense_ignore,
        amplifying_reaction_multiplier=reaction_multiplier,
        reaction_bonus=reaction_bonus,
        vulnerability_multiplier=vulnerability_multiplier,
    )
    print_json(result.to_dict())


@reaction_app.command("transformative")
def reaction_transformative(
    reaction: str = typer.Argument(..., help="swirl, overloaded, hyperbloom, burgeon, ..."),
    em: float = typer.Option(0.0, help="Maîtrise élémentaire"),
    level_multiplier: float = typer.Option(1446.85, help="Coefficient de niveau (90 par défaut)"),
    reaction_bonus: float = 0.0,
    resistance: float = 0.10,
) -> None:
    result = transformative_reaction(
        reaction=reaction,
        elemental_mastery=em,
        level_multiplier=level_multiplier,
        reaction_bonus=reaction_bonus,
        enemy_resistance=resistance,
    )
    print_json(result.to_dict())


@reaction_app.command("amplifying")
def reaction_amplifying(
    reaction: str = typer.Argument(
        ..., help="forward-vaporize, reverse-vaporize, forward-melt, reverse-melt"
    ),
    em: float = typer.Option(0.0, help="Maîtrise élémentaire"),
    reaction_bonus: float = 0.0,
) -> None:
    result = amplifying_multiplier(
        reaction=reaction, elemental_mastery=em, reaction_bonus=reaction_bonus
    )
    print_json(result.to_dict())


@leak_app.command("score")
def leak_score(
    provenance: float = typer.Option(..., min=0, max=5),
    evidence: float = typer.Option(..., min=0, max=5),
    corroboration: float = typer.Option(..., min=0, max=5),
    track_record: float = typer.Option(..., min=0, max=5),
    specificity: float = typer.Option(..., min=0, max=5),
    stage: DevelopmentStage = DevelopmentStage.UNKNOWN,
    conflict_penalty: float = typer.Option(0, min=0, max=20),
) -> None:
    result = score_leak(
        provenance=provenance,
        evidence=evidence,
        corroboration=corroboration,
        track_record=track_record,
        specificity=specificity,
        stage=stage,
        conflict_penalty=conflict_penalty,
    )
    print_json(result.to_dict())


@gcsim_app.command("run")
def gcsim_run(config: Path, open_viewer: bool = False) -> None:
    print_json(run_gcsim(config, open_viewer=open_viewer))


@app.command()
def doctor() -> None:
    """Auto-diagnostic : vérifie que l'installation Irminsul est complète."""
    import sys

    payload = system_status()
    index = payload["index"]
    repos = payload["repositories"]
    enabled = [r for r in repos if r["enabled"]]
    synced = [r for r in enabled if r["exists"]]
    checks: list[tuple[str, bool, str]] = [
        ("Python >= 3.11", sys.version_info[:2] >= (3, 11), ".".join(map(str, sys.version_info[:3]))),
        ("Binaire gcsim", gcsim_path().exists(), str(gcsim_path())),
        ("Index local construit", bool(index.get("exists")), f"{index.get('documents', 0)} documents"),
        (
            "Sources synchronisées",
            len(synced) == len(enabled) and bool(enabled),
            f"{len(synced)}/{len(enabled)} sources actives présentes",
        ),
    ]
    age = index.get("age_hours")
    if age is not None:
        fresh = age <= 24
        checks.append(("Fraîcheur index <= 24 h", fresh, f"{age} h"))

    table = Table(title="Irminsul AI — doctor")
    table.add_column("Contrôle")
    table.add_column("État")
    table.add_column("Détail")
    all_ok = True
    for label, ok, detail in checks:
        all_ok = all_ok and ok
        table.add_row(label, "OK" if ok else "À corriger", detail)
    console.print(table)
    if not all_ok:
        console.print(
            "[yellow]Des éléments manquent. Lance UPDATE_IRMINSUL.bat ou "
            "scripts/bootstrap.ps1 pour compléter l'installation.[/yellow]"
        )
    raise typer.Exit(code=0 if all_ok else 1)


def print_json(payload: object) -> None:
    console.print_json(json.dumps(payload, ensure_ascii=False, default=str))


if __name__ == "__main__":
    app()
