import configparser
from pathlib import Path
import os
import subprocess
import shutil
import importlib.resources as pkg_resources
from rich.console import Console
from .radar import TechRadar
from .utils.paths import get_default_app_dir
from . import examples  # package contenant zalando.md et zalando.xlsx
from . import templates  # package contenant radar.html.j2 et radar.css

console = Console()


def copy_example(example_name: str, dest_dir: Path):
    """Copie Markdown et Excel d'un exemple depuis le package vers le répertoire de l'application."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in [f"{example_name}.md", f"{example_name}.xlsx"]:
        source = pkg_resources.files(examples) / filename
        dest = dest_dir / filename
        if not dest.exists():
            with source.open("rb") as src_file, open(dest, "wb") as dst_file:
                shutil.copyfileobj(src_file, dst_file)


def copy_default_templates(dest_dir: Path):
    """Copie radar.html.j2 et radar.css depuis le package vers le répertoire de l'application."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in ["radar.html.j2", "radar.css"]:
        source = pkg_resources.files(templates) / filename
        dest = dest_dir / filename
        if not dest.exists():
            with source.open("rb") as src_file, open(dest, "wb") as dst_file:
                shutil.copyfileobj(src_file, dst_file)


class RadarLibrary:
    """Gestion d'une bibliothèque de radars via config_radars.ini."""

    def __init__(self, app_dir: str | Path | None = None):
        self.app_dir = Path(app_dir) if app_dir else get_default_app_dir()
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.app_dir / "config_radars.ini"

        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self._load_or_create()

    def _load_or_create(self):
        """Charge le fichier INI ou crée un radar Zalando opérationnel si absent."""
        input_dir = self.app_dir / "input"
        build_dir = self.app_dir / "build" / "zalando"
        templates_dir = self.app_dir / "templates"

        input_dir.mkdir(parents=True, exist_ok=True)
        build_dir.mkdir(parents=True, exist_ok=True)
        templates_dir.mkdir(parents=True, exist_ok=True)

        # Copier exemples et templates
        copy_example("zalando", input_dir)
        copy_default_templates(templates_dir)

        md_path = input_dir / "zalando.md"
        excel_path = input_dir / "zalando.xlsx"
        template_path = templates_dir / "radar.html.j2"
        css_path = templates_dir / "radar.css"
        output_path = build_dir / "index.html"

        # Ajouter le radar Zalando si le fichier config n'existe pas
        if not self.cache_path.exists():
            console.print("[dim]Création du fichier de configuration et du radar Zalando exemple.[/dim]")
            self.config["zalando"] = {
                "md_file_path": str(md_path),
                "excel_path": str(excel_path),
                "output_radar_path": str(output_path),
                "template_radar_path": str(template_path),
                "css_path": str(css_path)
            }
            self._save()
        else:
            self.config.read(self.cache_path, encoding="utf-8")

    def _save(self):
        with open(self.cache_path, "w", encoding="utf-8") as f:
            self.config.write(f)

    # --- Gestion des radars ---
    def add_radar(self, name: str, md_file_path: str, excel_path: str,
                  output_radar_path: str, template_radar_path: str | None = None,
                  css_path: str | None = None):
        self.config[name] = {
            "md_file_path": md_file_path,
            "excel_path": excel_path,
            "output_radar_path": output_radar_path,
            "template_radar_path": template_radar_path or "",
            "css_path": css_path or ""
        }
        self._save()
        console.print(f"[green]✅ Radar '{name}' ajouté/maj dans le cache.[/green]")

    def remove_radar(self, name: str):
        if name in self.config:
            self.config.remove_section(name)
            self._save()
            console.print(f"[green]🗑️ Radar '{name}' supprimé.[/green]")
        else:
            console.print(f"[red]Radar '{name}' introuvable.[/red]")

    def list_radars(self):
        if not self.config.sections():
            console.print("[dim]Aucun radar enregistré.[/dim]")
            return
        console.print("[bold cyan]📚 Radars disponibles :[/bold cyan]")
        for section in self.config.sections():
            console.print(f" - [bold]{section}[/bold] → {self.config[section]['output_radar_path']}")

    def get_radar(self, name: str) -> TechRadar | None:
        if name not in self.config:
            console.print(f"[red]Radar '{name}' introuvable.[/red]")
            return None
        data = self.config[name]
        return TechRadar(
            md_file_path=data.get("md_file_path", ""),
            excel_path=data.get("excel_path", ""),
            output_radar_path=data.get("output_radar_path", ""),
            template_radar_path=data.get("template_radar_path") or None,
            css_path=data.get("css_path") or None
        )

    # --- Fonctions utilitaires ---
    def open_config(self):
        """Ouvre le fichier config_radars.ini avec l'éditeur par défaut."""
        if not self.cache_path.exists():
            self._load_or_create()

        path = str(self.cache_path)
        try:
            if os.name == "nt":
                os.startfile(path)
            elif os.name == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            console.print(f"[red]Impossible d'ouvrir le fichier de config : {e}[/red]")

    def open_cache(self):
        """Ouvre le répertoire de l'application dans l'explorateur de fichiers."""
        try:
            path = str(self.app_dir)
            if os.name == "nt":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            console.print(f"[red]Impossible d'ouvrir le répertoire de l'application : {e}[/red]")

    def reset_app(self, config_only: bool = True):
        """
        Réinitialise le répertoire de l'application.
        Args:
            config_only (bool): 
                - True : supprime seulement le fichier config_radars.ini
                - False : supprime tout le répertoire de l'application
        """
        try:
            if config_only:
                if self.cache_path.exists():
                    self.cache_path.unlink()
                    console.print("[green]✅ Fichier config_radars.ini réinitialisé.[/green]")
                else:
                    console.print("[dim]Le fichier config_radars.ini n'existe pas.[/dim]")
            else:
                if self.app_dir.exists():
                    shutil.rmtree(self.app_dir)
                    console.print("[green]✅ Répertoire de l'application entièrement réinitialisé.[/green]")
                self.app_dir.mkdir(parents=True, exist_ok=True)
            
            # Recrée le radar exemple et templates
            self._load_or_create()
        except Exception as e:
            console.print(f"[red]Erreur lors de la réinitialisation : {e}[/red]")
