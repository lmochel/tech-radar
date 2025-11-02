import os
from jinja2 import Environment, FileSystemLoader

from .parser_excel import generate_tech_radar_data
from .parser_md import markdown_to_html_table


# ---------- Generate HTML ----------
def build_radar(md_file_path, excel_path, output_radar_path, template_radar_path, css_path):
    """
    Génère la page index.html du Tech Radar à partir :
      - du fichier Markdown (description)
      - du fichier Excel (données)
      - du template HTML Jinja2
      - du fichier CSS (optionnel, inline si trouvé)

    Si css_path est fourni et le fichier existe, le CSS est injecté directement dans la page.
    """

    # Charger le template
    template_dir = os.path.dirname(template_radar_path)
    template_file = os.path.basename(template_radar_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    # --- Générer les données du radar ---
    data = generate_tech_radar_data(excel_path)

    # --- Convertir le markdown en HTML table ---
    html_table = markdown_to_html_table(md_file_path)

    # --- Charger le CSS s'il existe ---
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # --- Rendu final ---
    rendered_html = template.render(
        metadata=data["metadata"],
        quadrants=data["quadrants"],
        rings=data["rings"],
        entries=data["entries"],
        html_table=html_table,
        css=css_content
    )

    # --- Sauvegarde du fichier ---
    os.makedirs(os.path.dirname(output_radar_path), exist_ok=True)
    with open(output_radar_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print(f"✅ index.html généré : {output_radar_path}")