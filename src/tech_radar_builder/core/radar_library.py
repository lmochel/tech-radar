import configparser
from pathlib import Path
import os
import subprocess
import shutil
import importlib.resources as pkg_resources
from rich.console import Console
from tech_radar_builder.core.radar import TechRadar
from tech_radar_builder.core.utils.paths import get_default_app_dir
from tech_radar_builder import examples  # contient zalando.md, generic.md, etc.
from tech_radar_builder import templates  # contient radar.html.j2 et radar.css

console = Console()


def copy_example(example_name: str, dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in [f"{example_name}.md", f"{example_name}.xlsx"]:
        source = pkg_resources.files(examples) / filename
        dest = dest_dir / filename
        if not dest.exists():
            with source.open("rb") as src_file, open(dest, "wb") as dst_file:
                shutil.copyfileobj(src_file, dst_file)


def copy_default_templates(dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in ["radar.html.j2", "radar.css"]:
        source = pkg_resources.files(templates) / filename
        dest = dest_dir / filename
        if not dest.exists():
            with source.open("rb") as src_file, open(dest, "wb") as dst_file:
                shutil.copyfileobj(src_file, dst_file)


class RadarLibrary:
    """Gestion de la bibliothèque de radars et initialisation de l’application."""

    def __init__(self, app_dir: str | Path | None = None):
        """Ne crée pas les répertoires, mais prépare les chemins essentiels."""
        self.app_dir = Path(app_dir) if app_dir else get_default_app_dir()

        # chemins internes
        self.input_dir = self.app_dir / "input"
        self.radar_dir = self.app_dir / "radar"
        self.templates_dir = self.app_dir / "templates"
        self.config_path = self.app_dir / "config_radars.ini"

        # Config
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # conserve la casse

        # Charger la config existante si elle existe
        if self.config_path.exists():
            self.config.read(self.config_path, encoding="utf-8")

    # ------------------------------------------------------------------
    # INITIALISATION COMPLÈTE
    # ------------------------------------------------------------------
    def init_app(self):
        """Crée la structure de l’application et initialise le radar exemple si nécessaire."""
        console.print("[dim]Initialisation du répertoire de l'application...[/dim]")

        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.radar_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Copier les templates de base
        copy_default_templates(self.templates_dir)

        # Copier le radar exemple "zalando" si aucun fichier config n’existe
        if not self.config_path.exists():
            console.print("[dim]Création du radar d'exemple Zalando...[/dim]")
            copy_example("zalando", self.input_dir)

            md_path = self.input_dir / "zalando.md"
            excel_path = self.input_dir / "zalando.xlsx"
            template_path = self.templates_dir / "radar.html.j2"
            css_path = self.templates_dir / "radar.css"
            output_path = self.radar_dir / "zalando_radar.html"

            self.config["zalando"] = {
                "md_file_path": str(md_path),
                "excel_path": str(excel_path),
                "output_radar_path": str(output_path),
                "template_radar_path": str(template_path),
                "css_path": str(css_path),
            }
            self._save()
            console.print("[green]✅ Application initialisée avec le radar Zalando d'exemple.[/green]")
        else:
            console.print("[yellow]⚠️ Le fichier de configuration existe déjà, aucune réécriture effectuée.[/yellow]")

    # ------------------------------------------------------------------
    # GESTION CONFIG
    # ------------------------------------------------------------------
    def _save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            self.config.write(f)

    # ------------------------------------------------------------------
    # FONCTIONS UTILITAIRES
    # ------------------------------------------------------------------
    def open_config(self):
        """Ouvre le fichier config_radars.ini avec l’éditeur par défaut."""
        if not self.config_path.exists():
            console.print("[red]Aucune configuration trouvée. Exécutez `radar init` d'abord.[/red]")
            return

        path = str(self.config_path)
        try:
            if os.name == "nt":
                os.startfile(path)
            elif os.name == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            console.print(f"[red]Erreur : impossible d’ouvrir le fichier de config : {e}[/red]")

    def open_app_dir(self):
        """Ouvre le dossier principal de l'application."""
        try:
            path = str(self.app_dir)
            if os.name == "nt":
                os.startfile(path)
            elif os.name == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            console.print(f"[red]Erreur : impossible d’ouvrir le répertoire de l'application : {e}[/red]")

    # --- Méthodes radar ---
    def new(
        self,
        name: str,
        md_file_path: str | None = None,
        excel_path: str | None = None,
        template_radar_path: str | None = None,
        css_path: str | None = None,
    ) -> TechRadar:
        """Crée un nouveau radar."""
        name = name.lower()
        md_target = self.input_dir / f"{name}.md"
        excel_target = self.input_dir / f"{name}.xlsx"
        output_path = self.radar_dir / f"{name}_radar.html"

        # Markdown
        if md_file_path:
            shutil.copy(md_file_path, md_target)
        elif not md_target.exists():
            generic_md = pkg_resources.files(examples) / "generic.md"
            with generic_md.open("rb") as src_file, open(md_target, "wb") as dst_file:
                shutil.copyfileobj(src_file, dst_file)

        # Excel
        if excel_path:
            shutil.copy(excel_path, excel_target)
        elif not excel_target.exists():
            generic_xlsx = pkg_resources.files(examples) / "generic.xlsx"
            with generic_xlsx.open("rb") as src_file, open(excel_target, "wb") as dst_file:
                shutil.copyfileobj(src_file, dst_file)

        # Config
        self.config[name] = {
            "md_file_path": str(md_target),
            "excel_path": str(excel_target),
            "output_radar_path": str(output_path),
            "template_radar_path": template_radar_path or str(self.templates_dir / "radar.html.j2"),
            "css_path": css_path or str(self.templates_dir / "radar.css"),
        }
        self._save()
        console.print(f"[green]✅ Radar '{name}' ajouté/maj dans le cache.[/green]")

        return TechRadar(
            md_file_path=md_target,
            excel_path=excel_target,
            output_radar_path=output_path,
            template_radar_path=template_radar_path or str(self.templates_dir / "radar.html.j2"),
            css_path=css_path or str(self.templates_dir / "radar.css"),
        )

    def remove(self, name: str, delete_inputs: bool = False):
        """Supprime un radar et éventuellement ses fichiers sources."""
        name = name.lower()
        if name not in self.config:
            console.print(f"[red]Radar '{name}' introuvable.[/red]")
            return

        output_path = Path(self.config[name]["output_radar_path"])
        if output_path.exists():
            output_path.unlink()
            console.print(f"[blue]🗑️ HTML '{output_path.name}' supprimé.[/blue]")

        if delete_inputs:
            for p in [self.input_dir / f"{name}.md", self.input_dir / f"{name}.xlsx"]:
                if p.exists():
                    p.unlink()
                    console.print(f"[blue]🗑️ Fichier '{p.name}' supprimé.[/blue]")

        self.config.remove_section(name)
        self._save()
        console.print(f"[green]✅ Radar '{name}' supprimé du cache.[/green]")

    def refresh(self, name: str):
        """Supprime le HTML existant et reconstruit le radar."""
        name = name.lower()
        if name not in self.config:
            console.print(f"[red]Radar '{name}' introuvable.[/red]")
            return

        output_path = Path(self.config[name]["output_radar_path"])
        if output_path.exists():
            output_path.unlink()
            console.print(f"[blue]🗑️ HTML '{output_path.name}' supprimé pour refresh.[/blue]")

        radar = self.get(name)
        if radar:
            radar.build()
            console.print(f"[green]✅ Radar '{name}' rafraîchi.[/green]")

    def get(self, name: str) -> TechRadar | None:
        """Retourne un objet TechRadar."""
        if name not in self.config:
            console.print(f"[red]Radar '{name}' introuvable.[/red]")
            return None
        data = self.config[name]
        return TechRadar(
            md_file_path=data.get("md_file_path", ""),
            excel_path=data.get("excel_path", ""),
            output_radar_path=data.get("output_radar_path", ""),
            template_radar_path=data.get("template_radar_path") or None,
            css_path=data.get("css_path") or None,
        )

    def list(self):
        """Affiche tous les radars enregistrés dans le cache."""
        sections = self.config.sections()
        if not sections:
            console.print("[dim]Aucun radar enregistré.[/dim]")
            return

        console.print("[bold cyan]📚 Radars disponibles :[/bold cyan]")
        for section in sections:
            data = self.config[section]
            output_path = data.get("output_radar_path", "—")
            console.print(f" - [bold]{section}[/bold] → {output_path}")

    def reset(self, config_only: bool = True):
        """Réinitialise le répertoire de l'application, avec option config_only."""
        try:
            if config_only:
                if self.cache_path.exists():
                    self.cache_path.unlink()
                    console.print("[green]✅ Fichier config_radars.ini réinitialisé.[/green]")
            else:
                if self.app_dir.exists():
                    shutil.rmtree(self.app_dir)
                    console.print("[green]✅ Répertoire de l'application entièrement réinitialisé.[/green]")
                self.app_dir.mkdir(parents=True, exist_ok=True)

            self._load_or_create()
        except Exception as e:
            console.print(f"[red]Erreur lors de la réinitialisation : {e}[/red]")
