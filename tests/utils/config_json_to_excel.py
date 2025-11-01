import json
import pandas as pd

# --- 1. Chargement du fichier config.json ---
with open("tests\output\config.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# --- 2. Création du DataFrame ---
df = pd.DataFrame(data["entries"])

# --- 3. Mappings pour lisibilité ---
quadrant_map = {
    0: "Languages & Frameworks",
    1: "Infrastructure",
    2: "Data Management",
    3: "Data Engineering, Streaming & Analytics"
}

ring_map = {
    0: "Adopt",
    1: "Trial",
    2: "Assess",
    3: "Hold"
}

moved_map = {
    -1: "Moved Down",
    0: "No Change",
    1: "Moved Up"
}

df["quadrant_name"] = df["quadrant"].map(quadrant_map)
df["ring_name"] = df["ring"].map(ring_map)
df["moved_status"] = df["moved"].map(moved_map)

# --- 4. Transformation colonne active ---
df["active_display"] = df["active"].apply(lambda x: "X" if x else "")

# --- 5. Sélection et renommage des colonnes ---
final_df = df[["label", "quadrant_name", "ring_name", "moved_status", "link", "active_display"]].rename(
    columns={
        "label": "Label",
        "quadrant_name": "Quadrant",
        "ring_name": "Ring",
        "moved_status": "Status",
        "link": "Link",
        "active_display": "Active"
    }
)

# --- 6. Export vers Excel ---
final_df.to_excel("tech_radar_clean.xlsx", index=False)

print("✅ Fichier 'tech_radar_clean.xlsx' généré avec succès !")
