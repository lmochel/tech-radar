import markdown


def markdown_to_html_table(md_file_path):
    """
    Convertit un fichier Markdown en HTML avec une table à une ligne et deux colonnes.
    Utilise '---' comme séparateur entre les colonnes.
    """
    # Lire le contenu du fichier Markdown
    with open(md_file_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Séparer en colonnes à partir du séparateur visuel '---'
    # On suppose que chaque '---' correspond à un passage à la colonne suivante
    columns_md = md_content.split('---')

    # Convertir chaque bloc Markdown en HTML
    columns_html = [markdown.markdown(col.strip()) for col in columns_md]

    # Construire la table HTML
    table_html = "<table>\n<tr>\n"
    for col_html in columns_html:
        table_html += f"<td>\n{col_html}\n</td>\n"
    table_html += "</tr>\n</table>"

    return table_html    