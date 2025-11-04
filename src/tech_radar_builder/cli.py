import typer
from rich.console import Console
from tech_radar_builder import radars

app = typer.Typer(help="Outil CLI pour gérer vos Tech Radars")
console = Console()


@app.command()
def init():
    """
    Initialise l'application :
    - crée les répertoires nécessaires
    - copie les templates
    - crée le radar exemple Zalando si aucune config existante
    """
    radars.init_app()


@app.command()
def list():
    """Liste tous les radars enregistrés."""
    sections = radars.config.sections()
    if not sections:
        console.print("[yellow]Aucun radar enregistré.[/yellow]")
        return
    console.print("[bold underline]Radars disponibles :[/bold underline]")
    for name in sections:
        output = radars.config[name].get("output_radar_path", "")
        console.print(f"• {name} → {output}")


@app.command()
def new(name: str, md_file: str = None, excel_file: str = None):
    """Crée un nouveau radar."""
    radars.new(name, excel_file, md_file)
    console.print(f"[green]Radar '{name}' créé avec succès.[/green]")


@app.command()
def refresh(name: str):
    """Reconstruit le radar (supprime et régénère le fichier index)."""
    radars.refresh(name)
    console.print(f"[green]Radar '{name}' régénéré avec succès.[/green]")


@app.command()
def remove(name: str, delete_inputs: bool = typer.Option(False, help="Supprime aussi les fichiers d’entrée")):
    """Supprime un radar (et éventuellement ses fichiers d’entrée)."""
    radars.remove(name, delete_inputs=delete_inputs)
    console.print(f"[red]Radar '{name}' supprimé.[/red]")


@app.command()
def serve(name: str, port: int = 8000):
    """Lance un serveur local pour visualiser un radar."""
    from tech_radar_builder.core.utils.server import serve_html

    radar = radars.get(name)
    if not radar:
        console.print(f"[red]Radar '{name}' introuvable ou non construit.[/red]")
        raise typer.Exit(1)

    # Rebuild si nécessaire
    radar.build()
    serve_html(radar.output_radar_path, port=port)


@app.command()
def open_config():
    """Ouvre le fichier de configuration dans l’éditeur par défaut."""
    radars.open_config()


@app.command()
def open_app_dir():
    """Ouvre le dossier de l'application dans l'explorateur."""
    radars.open_app_dir()


@app.command()
def reset(config_only: bool = typer.Option(True, help="Ne supprime que le fichier config")):
    """Réinitialise l’application."""
    radars.reset(config_only=config_only)
    console.print("[red]Application réinitialisée.[/red]")


if __name__ == "__main__":
    app()
