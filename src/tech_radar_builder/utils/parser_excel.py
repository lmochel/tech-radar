import pandas as pd
from openpyxl import load_workbook
import re


def clean_field_name(name: str) -> str:
    """
    Nettoie un nom de champ Excel en format snake_case (minuscule, underscore, sans ponctuation).
    Exemple : "Repo url:" -> "repo_url"
    """
    name = str(name).strip().lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)  # remplace tout sauf lettres/chiffres par "_"
    name = re.sub(r'_+', '_', name)           # évite les doublons d'underscore
    return name.strip('_')                    # supprime underscores en trop


def generate_metadata_from_excel(excel_path, sheet_name="Metadata"):
    """
    Lit un onglet Excel contenant deux colonnes : Champ / Valeur
    Exemple :
        | Field        | Value                       |
        |---------------|-----------------------------|
        | Title:        | My Tech Radar               |
        | Description:  | Example radar visualization |
        | Repo url:     | https://github.com/monrepo  |

    Retourne :
        {
          "title": "My Tech Radar",
          "description": "Example radar visualization",
          "repo_url": "https://github.com/monrepo"
        }
    """
    wb = load_workbook(excel_path, data_only=True)
    ws = wb[sheet_name]

    metadata = {}
    for row in ws.iter_rows(min_row=1, values_only=True):
        if not row[0] or not row[1]:
            continue
        key = clean_field_name(row[0])
        value = str(row[1]).strip()
        metadata[key] = value

    return metadata


def get_hex_from_fill(cell):
    """
    Extrait la couleur de fond (fill) d'une cellule Excel au format hexadécimal.
    Retourne None si la cellule n'a pas de couleur définie.
    """
    fill = cell.fill
    if fill and fill.fgColor and fill.fgColor.type == "rgb" and fill.fgColor.rgb:
        rgb = fill.fgColor.rgb
        # Supprimer l'alpha s'il existe (ex: 'FF5BA300' -> '#5BA300')
        return f"#{rgb[-6:]}"
    return None


def generate_rings_from_excel(excel_path, sheet_name="Zones"):
    """
    Lit l'onglet 'Zones' et retourne la liste des rings sous la forme :
    [
      { "name": "ADOPT", "color": "#5ba300", "rank": 0 },
      { "name": "TRIAL", "color": "#009eb0", "rank": 1 },
      ...
    ]
    """
    wb = load_workbook(excel_path, data_only=True)
    ws = wb[sheet_name]

    # Trouver les colonnes par nom
    headers = {cell.value: idx for idx, cell in enumerate(next(ws.iter_rows(min_row=1, max_row=1)))}

    rings = []
    for row in ws.iter_rows(min_row=2):
        zone_cell = row[headers["Zone"]]
        rank_cell = row[headers["Rank"]]
        color_cell = row[headers["Color"]]

        if zone_cell.value is None or rank_cell.value is None:
            continue

        color_hex = get_hex_from_fill(color_cell) or "#cccccc"  # Valeur par défaut si aucune couleur
        name = str(zone_cell.value).strip()
        rank = int(rank_cell.value)

        rings.append({
            "name": name,
            "color": color_hex,
            "rank": rank
        })

    # Trier les rings par rang croissant
    rings = sorted(rings, key=lambda x: x["rank"])

    return rings

def generate_quadrants_from_excel(excel_path, sheet_name="Sectors"):
    """
    Lit l'onglet 'Sectors' et retourne la liste des quadrants sous forme :
    [
      { "name": "Techniques", "quadrant": 0 },
      { "name": "Outils", "quadrant": 1 },
      ...
    ]
    """
    wb = load_workbook(excel_path, data_only=True)
    ws = wb[sheet_name]

    # Trouver les colonnes par nom
    headers = {cell.value: idx for idx, cell in enumerate(next(ws.iter_rows(min_row=1, max_row=1)))}

    quadrants = []
    for row in ws.iter_rows(min_row=2):
        num_cell = row[headers["#"]]
        name_cell = row[headers["Sector"]]

        if num_cell.value is None or name_cell.value is None:
            continue

        # Attention : le radar JS utilise un index de quadrant à partir de 0
        quadrant_index = int(num_cell.value) - 1

        quadrants.append({
            "quadrant": quadrant_index,
            "name": str(name_cell.value).strip()
        })

    # Tri par numéro
    quadrants = sorted(quadrants, key=lambda x: x["quadrant"])

    return quadrants

def generate_entries_from_tech_list(excel_path, sheet_name="Tech. List"):
    """
    Lit l'onglet 'Tech. List' et retourne une liste de dictionnaires avec :
    Active, Technology, Tech. Sector, Monitoring Zone, Trend, Link, Comment.

    Les cellules vides sont converties en None.
    La colonne Active devient True si 'X', sinon False.
    """
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # Transformer la colonne Active : 'X' -> True, sinon False
    df["Active"] = df["Active"].apply(lambda x: True if str(x).strip().upper() == "X" else False)

    # Forcer toutes les colonnes en type object pour pouvoir remplacer NaN
    df = df.astype(object)

    # Remplacer tous les NaN par None
    df = df.where(pd.notna(df), None)

    # Convertir en liste de dictionnaires
    entries = df.to_dict(orient="records")

    return entries

def generate_tech_radar_data(excel_path):
    """
    Construit le dictionnaire complet Tech Radar à partir d'un fichier Excel,
    en réutilisant les fonctions déjà existantes :
    - generate_metadata_from_excel
    - generate_quadrants_from_excel
    - generate_rings_from_excel
    - generate_entries_from_tech_list
    """
    # -------------------- METADATA --------------------
    metadata = generate_metadata_from_excel(excel_path)
    
    # -------------------- QUADRANTS --------------------
    quadrants = generate_quadrants_from_excel(excel_path)
    quadrant_to_number = {item['name']: item['quadrant'] for item in quadrants}
    
    # -------------------- RINGS --------------------
    rings = generate_rings_from_excel(excel_path)
    ring_to_number = {item['name']: item['rank'] for item in rings}
    for item in rings:
        if "name" in item and item["name"] is not None:
            item["name"] = item["name"].upper()
    
    # -------------------- ENTRIES --------------------
    entries_raw = generate_entries_from_tech_list(excel_path)
    
    # Mapping des colonnes pour correspondre au format Tech Radar
    trend_to_moved = {
        "Moved out (▼)": -1,
        "No change (●)": 0,
        "Moved in (▲)": 1,
        "New (*)": 2
    }
    
    entries = []
    for row in entries_raw:
        entry = {
            "active": row.get("Active", False),
            "label": row.get("Technology"),
            "quadrant": quadrant_to_number.get((row.get("Tech. Sector"))),
            "ring": ring_to_number.get((row.get("Monitoring Zone"))),
            "link": row.get("Link", None),
            "moved": trend_to_moved.get(str(row.get("Trend")).strip(), 0)
        }
        entries.append(entry)
    
    # -------------------- ASSEMBLE --------------------
    data = {
        "metadata": metadata,
        "quadrants": [{k: v for k, v in q.items() if k != "quadrant"} for q in quadrants],
        "rings": [{k: v for k, v in r.items() if k != "rank"} for r in rings],
        "entries": entries
    }
    
    return data

