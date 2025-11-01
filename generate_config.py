import pandas as pd
import json

def generate_config(excel_path, output_path):

    # Lire la première ligne pour récupérer la date
    first_row = pd.read_excel(excel_path, nrows=1, header=None)
    date_value = str(first_row.iloc[0, 1])  # Colonne B de la première ligne

    # Lire le reste du fichier (les données)
    df = pd.read_excel(excel_path, skiprows=1)

    # Conversion des colonnes Quadrant et Ring en valeurs numériques dynamiques
    df["quadrant_num"] = df["Quadrant"].apply(lambda x: int(str(x).split(".")[0].strip())-1)
    df["ring_num"] = df["Ring"].apply(lambda x: int(str(x).split(".")[0].strip()))

    # Mapping texte Status → moved numérique
    status_to_moved = {
        "Moved out (▼)": -1,
        "No change (●)": 0,
        "Moved in (▲)": 1,
        "New (*)": 2
    }

    # Construction des entries
    entries = []
    for _, row in df.iterrows():
        moved_value = status_to_moved.get(str(row["Status"]).strip(), 0)

        # Construire l'entrée avec link juste après label
        entry = {
            "quadrant": row["quadrant_num"],
            "ring": row["ring_num"],
            "label": row["Label"],
            "link": row["Link"] if pd.notna(row.get("Link")) else None,
            "active": True if row["Active"] == "X" else False,
            "moved": moved_value
        }

        # Si link est None, on peut la supprimer pour garder le JSON propre
        if entry["link"] is None:
            entry.pop("link")

        entries.append(entry)

    # Générer le JSON final
    config_json = {
        "date": date_value,
        "entries": entries
    }

    # Écrire le fichier config.json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config_json, f, indent=2, ensure_ascii=False)

    print(f"✅ Fichier {output_path} généré avec succès avec la date {date_value} !")

if __name__ == "__main__":
    generate_config(
        excel_path=r"tests\input\tech_radar.xlsx",
        output_path="config_generated_from_excel.json"
    )
