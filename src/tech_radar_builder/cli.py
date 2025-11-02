import click
from rich.console import Console
from .builder import init_project, add_radar

console = Console()

@click.group()
def main():
    """Tech Radar Builder CLI."""
    pass

@main.command()
@click.argument("appdir", type=click.Path())
def init(appdir):
    """Initialise un nouveau projet Tech Radar dans APPDIR."""
    init_project(appdir)
    console.print(f"[green]Projet initialisé dans {appdir}[/green]")

@main.command()
@click.argument("name")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_md", type=click.Path())
@click.argument("output_html", type=click.Path())
def add(name, input_file, output_md, output_html):
    """Ajoute un radar depuis un fichier d’entrée et génère HTML/MD."""
    add_radar(name, input_file, output_md, output_html)
    console.print(f"[cyan]Radar {name} généré avec succès[/cyan]")
