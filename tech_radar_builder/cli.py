import os
import argparse
from pathlib import Path
import appdirs
import configparser

# ------------------ Import de tes fonctions existantes ------------------
from tech_radar_builder.radar_builder import generate_index_html

APP_NAME = "Tech Radar"
APP_AUTHOR = "lmochel"  # ou ton organisation

config_dir = Path(appdirs.user_data_dir(APP_NAME, APP_AUTHOR))
config_dir.mkdir(parents=True, exist_ok=True)
config_path = config_dir / "config.ini"

# ------------------ Gestion de la configuration ------------------
def init_config():
    """
    Crée le fichier config.ini si il n'existe pas,
    et copie un template HTML et CSS par défaut dans l'appdir.
    """
    if config_path.exists():
        print(f"⚠️  Le fichier de config existe déjà : {config_path}")
        return

    # Créer le dossier pour les fichiers statiques si nécessaire
    static_dir = config_dir / "static"
    static_dir.mkdir(exist_ok=True)

    # Fichiers par défaut
    template_default_path = static_dir / "index_template.html"
    css_default_path = static_dir / "radar.css"

    # Copier les fichiers par défaut (ou créer des fichiers simples si non fournis)
    if not template_default_path.exists():
        template_default_path.write_text("""
<!DOCTYPE html>
<html lang="en">

<head>
<meta http-equiv="Content-type" content="text/html; charset=utf-8">
<meta name="description" content="{{ metadata.description }}">
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{{ metadata.title }}</title>
<link rel="shortcut icon" href="{{ metadata.icon }}">

<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://zalando.github.io/tech-radar/release/radar-0.12.js"></script>

<link rel="stylesheet" href="radar.css">
</head>

<body>

<svg id="radar"></svg>

<script>
const entries = {{ entries | tojson }};
const rings = {{ rings | tojson }};
const quadrants = {{ quadrants | tojson }};
radar_visualization({
  repo_url: "{{ metadata.repo_url }}",
  title: "{{ metadata.title }}",
  date: "{{ metadata.date }}",
  quadrants: quadrants,
  rings: rings,
  entries: entries
});
</script>

{{ html_table | safe }}

</body>
</html>
""", encoding="utf-8")

    if not css_default_path.exists():
        css_default_path.write_text("""
/* CSS de base pour le Tech Radar */
body {
  font-family: 'Source Sans Pro', arial, helvetica, sans-serif;
  padding-bottom: 50px;
}
h3 {
  margin-top: 50px;
}
li {
  margin: 25px 50px 0 0;
}
table {
  width: 1400px;
  margin: 0 50px 0 50px;
}
td {
  width: 50%;
  vertical-align: top;
  padding-right: 60px;
}
.hover-underline {
  text-decoration: none;
}
.hover-underline:hover {
  text-decoration: underline;
}
""", encoding="utf-8")

    # Créer le fichier config.ini
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'template_file': str(template_default_path),
        'css_file': str(css_default_path)
    }

    with open(config_path, "w", encoding="utf-8") as f:
        config.write(f)

    print(f"✅ Fichier de config créé : {config_path}")
    print(f"Fichiers par défaut : template -> {template_default_path}, css -> {css_default_path}")


def add_radar(radar_name, excel_file, markdown_file, template_file, output_file):
    config = configparser.ConfigParser()
    config.read(config_path)

    if radar_name in config.sections():
        print(f"⚠️ Le radar '{radar_name}' existe déjà.")
        return

    config[radar_name] = {
        "excel_file": excel_file,
        "markdown_file": markdown_file,
        "template_file": template_file,
        "output_file": output_file
    }

    with open(config_path, "w", encoding="utf-8") as f:
        config.write(f)

    print(f"✅ Radar '{radar_name}' ajouté à la config.")


def remove_radar(radar_name):
    config = configparser.ConfigParser()
    config.read(config_path)

    if radar_name not in config.sections():
        print(f"❌ Le radar '{radar_name}' n’existe pas.")
        return

    config.remove_section(radar_name)
    with open(config_path, "w", encoding="utf-8") as f:
        config.write(f)

    print(f"✅ Radar '{radar_name}' supprimé de la config.")


def update_radar(radar_name, excel_file=None, markdown_file=None, template_file=None, output_file=None):
    config = configparser.ConfigParser()
    config.read(config_path)

    if radar_name not in config.sections():
        print(f"❌ Le radar '{radar_name}' n’existe pas.")
        return

    section = config[radar_name]
    if excel_file:
        section["excel_file"] = excel_file
    if markdown_file:
        section["markdown_file"] = markdown_file
    if template_file:
        section["template_file"] = template_file
    if output_file:
        section["output_file"] = output_file

    with open(config_path, "w", encoding="utf-8") as f:
        config.write(f)

    print(f"✅ Radar '{radar_name}' mis à jour.")


def build_radar(radar_name):
    config = configparser.ConfigParser()
    config.read(config_path)

    if radar_name not in config.sections():
        print(f"❌ Le radar '{radar_name}' n’existe pas.")
        return

    cfg = config[radar_name]
    excel_file = cfg.get("excel_file")
    markdown_file = cfg.get("markdown_file")
    template_file = cfg.get("template_file")
    output_file = cfg.get("output_file")

    generate_index_html(markdown_file, excel_file, template_file, output_file)
    print(f"✅ Radar '{radar_name}' généré : {output_file}")


# ------------------ CLI ------------------
def main():
    parser = argparse.ArgumentParser(description="Tech Radar CLI")
    subparsers = parser.add_subparsers(dest="command")

    # init
    subparsers.add_parser("init", help="Créer le fichier de config")

    # add
    add_parser = subparsers.add_parser("add", help="Ajouter un radar")
    add_parser.add_argument("radar_name")
    add_parser.add_argument("excel_file")
    add_parser.add_argument("markdown_file")
    add_parser.add_argument("template_file")
    add_parser.add_argument("output_file")

    # remove
    remove_parser = subparsers.add_parser("remove", help="Supprimer un radar")
    remove_parser.add_argument("radar_name")

    # update
    update_parser = subparsers.add_parser("update", help="Mettre à jour un radar")
    update_parser.add_argument("radar_name")
    update_parser.add_argument("--excel_file")
    update_parser.add_argument("--markdown_file")
    update_parser.add_argument("--template_file")
    update_parser.add_argument("--output_file")

    # build
    build_parser = subparsers.add_parser("build", help="Générer un radar")
    build_parser.add_argument("radar_name")

    args = parser.parse_args()

    if args.command == "init":
        init_config()
    elif args.command == "add":
        add_radar(args.radar_name, args.excel_file, args.markdown_file, args.template_file, args.output_file)
    elif args.command == "remove":
        remove_radar(args.radar_name)
    elif args.command == "update":
        update_radar(args.radar_name, args.excel_file, args.markdown_file, args.template_file, args.output_file)
    elif args.command == "build":
        build_radar(args.radar_name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
