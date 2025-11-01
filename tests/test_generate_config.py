import json
from generate_config import generate_config

def test_config_generation():
    # Chemins
    excel_path = r"tests\input\tech_radar.xlsx"
    output_path = r"config_generated_from_excel.json"
    reference_path = r"tests\output\config.json"

    # Générer le config.json
    generate_config(excel_path, output_path)

    # Charger le JSON généré et le JSON de référence
    with open(output_path, "r", encoding="utf-8") as f:
        generated = json.load(f)

    with open(reference_path, "r", encoding="utf-8") as f:
        reference = json.load(f)

    # Comparer les deux fichiers
    assert generated == reference, "Le config.json généré ne correspond pas au config.json de référence."
