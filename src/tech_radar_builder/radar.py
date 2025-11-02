from pathlib import Path
from rich.console import Console
from .utils.radar_generator import build_radar
from .utils.server import serve_html
import time

console = Console()

class TechRadar:

    def __init__(self,
                 md_file_path: str,
                 excel_path: str,
                 output_radar_path: str,
                 template_radar_path: str | None = None,
                 css_path: str | None = None
                 ):
        self.md_file_path = Path(md_file_path)
        self.excel_path = Path(excel_path)
        self.output_radar_path = Path(output_radar_path)
        self.template_radar_path = Path(template_radar_path) if template_radar_path else None
        self.css_path = Path(css_path) if css_path else None

    def build(self):
        """Génère le HTML du radar à partir du Markdown et de l'Excel."""
        build_radar(
            md_file_path=str(self.md_file_path),
            excel_path=str(self.excel_path),
            output_radar_path=str(self.output_radar_path),
            template_radar_path=str(self.template_radar_path) if self.template_radar_path else None,
            css_path=str(self.css_path) if self.css_path else None
        )
        console.print(f"[green]✅ HTML généré : {self.output_radar_path}[/green]")

    def serve(self, port: int | None = None, watch: bool = False, poll_interval: float = 1.0):
        """
        Sert le radar via un serveur local.
        
        Args:
            port (int | None): Port du serveur, défaut 8000.
            watch (bool): Si True, régénère automatiquement le HTML si Markdown/Excel change.
            poll_interval (float): Intervalle de vérification en secondes en mode watch.
        """
        html_path = self.output_radar_path
        md_path = self.md_file_path
        excel_path = self.excel_path

        # Génération initiale si HTML absent
        if not html_path.exists():
            console.print("[yellow]Le fichier HTML n'existe pas, génération automatique...[/yellow]")
            self.build()

        # Serve simple sans watch
        if not watch:
            serve_html(str(html_path), port=port)
            return

        # --- Watch mode ---
        console.print("[blue]Mode watch activé : le radar sera régénéré si Markdown ou Excel change.[/blue]")

        last_md_mtime = md_path.stat().st_mtime
        last_excel_mtime = excel_path.stat().st_mtime

        # Lancer le serveur dans un thread séparé pour garder la boucle watch
        import threading
        server_thread = threading.Thread(target=serve_html, args=(str(html_path), port), daemon=True)
        server_thread.start()

        try:
            while True:
                current_md_mtime = md_path.stat().st_mtime
                current_excel_mtime = excel_path.stat().st_mtime

                if current_md_mtime != last_md_mtime or current_excel_mtime != last_excel_mtime:
                    console.print("[green]Changement détecté, reconstruction du HTML...[/green]")
                    self.build()
                    last_md_mtime = current_md_mtime
                    last_excel_mtime = current_excel_mtime

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            console.print("\n🛑 [bold yellow]Arrêt du watch server...[/bold yellow]")
