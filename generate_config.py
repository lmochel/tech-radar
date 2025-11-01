import pandas as pd
import json

def generate_config(excel_path, output_path):

    # Lire la première ligne pour récupérer la date
    first_row = pd.read_excel(excel_path, nrows=1, header=None)
    date_value = str(first_row.iloc[0, 1])  # Colonne B de la première ligne

    # Lire le reste du fichier (les données)
    df = pd.read_excel(excel_path, skiprows=1)

    # --- 2. Conversion des colonnes Quadrant et Ring en valeurs numériques dynamiques ---
    # Exemple : "1. Languages" → 1
    df["quadrant_num"] = df["Quadrant"].apply(lambda x: int(str(x).split(".")[0].strip()))
    df["ring_num"] = df["Ring"].apply(lambda x: int(str(x).split(".")[0].strip()))

    # --- 3. Mapping texte Status → moved numérique ---
    status_to_moved = {
        "Moved out (▼)": -1,
        "No change (●)": 0,
        "Moved in (▲)": 1,
        "New (*)": 2
    }

    # --- 4. Construction des entries ---
    entries = []
    for _, row in df.iterrows():
        moved_value = status_to_moved.get(str(row["Status"]).strip(), 0)  # fallback à 0
        entry = {
            "quadrant": row["quadrant_num"],
            "ring": row["ring_num"],
            "label": row["Label"],
            "active": True if row["Active"] == "X" else False,
            "moved": moved_value
        }
        if pd.notna(row.get("Link")):
            entry["link"] = row["Link"]
        entries.append(entry)

    # --- 5. Générer le JSON final ---
    config_json = {
        "date": date_value,
        "entries": entries
    }

    # --- 6. Écrire le fichier config.json ---
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config_json, f, indent=2, ensure_ascii=False)

    print(f"✅ Fichier {output_path} généré avec succès avec la date {date_value} !")

if __name__ == "__main__":
    generate_config(
        excel_path = r"tests\input\tech_radar.xlsx",
        output_path="config_generated_from_excel.json"
    )