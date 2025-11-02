import http.server
import socket
import socketserver
import webbrowser
import os
import sys
from pathlib import Path
from rich.console import Console

console = Console()


def find_free_port(start=8000, end=9000):
    """Trouve un port libre dans la plage spécifiée."""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("Aucun port libre trouvé entre 8000 et 9000.")


def serve_html(html_path: str, port: int | None = None):
    """
    Lance un serveur HTTP local pour visualiser un fichier HTML.
    - Ouvre automatiquement le navigateur par défaut.
    - S'arrête proprement avec Ctrl+C.
    """
    html_path = Path(html_path).resolve()
    if not html_path.exists():
        console.print(f"[red]Erreur : le fichier '{html_path}' est introuvable.[/red]")
        sys.exit(1)

    directory = html_path.parent
    filename = html_path.name
    port = port or find_free_port()

    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/{filename}"
        console.print(f"🌐 [bold green]Serveur local actif[/bold green] sur [underline]{url}[/underline]")
        console.print("[dim]Appuyez sur Ctrl+C pour arrêter le serveur.[/dim]")

        # Ouvre le navigateur
        webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n🛑 [bold yellow]Arrêt du serveur local...[/bold yellow]")
            httpd.server_close()
