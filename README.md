# Tech Radar Builder

Tech Radar Builder est un outil Python pour créer, gérer et visualiser des Tech Radars (à l'image du [Zalando Tech Radar](https://opensource.zalando.com/tech-radar/)).  
Il fournit à la fois une **API Python** et une **interface en ligne de commande (CLI)**.

---

## Installation

### 1. Pré-requis

- Python 3.10 ou supérieur
- Pip (ou pipx pour la CLI)

---

### 2. Installation depuis GitHub

#### Avec pip (directement depuis le repo)

```bash
pip install git+https://github.com/lmochel/tech-radar-builder.git
```

#### Ou en mode développement (editable)

```bash
git clone https://github.com/lmochel/tech-radar-builder.git
cd tech-radar-builder
pip install -e .
```

L’option -e permet de modifier le code et de voir les changements immédiatement.

### 3. Installation avec pipx (optionnel pour CLI)

pipx permet d’installer l’application dans un environnement isolé :

```bash
pipx install git+https://github.com/lmochel/tech-radar-builder.git

```

## Utilisation en ligne de commande

Après installation, la commande radar est disponible dans cmd ou PowerShell.

### Commandes principales

| Commande                      | Description                                                   |
| ----------------------------- | ------------------------------------------------------------- |
| `radar init`                  | Initialise le répertoire de l’application avec radar exemple. |
| `radar list`                  | Liste tous les radars enregistrés.                            |
| `radar new NAME`              | Crée un nouveau radar (optionnel : fichiers Markdown/Excel).  |
| `radar refresh NAME`          | Reconstruit le HTML du radar.                                 |
| `radar remove NAME`           | Supprime le radar et optionnellement les fichiers d’entrée.   |
| `radar serve NAME`            | Lance un serveur local pour visualiser le radar.              |
| `radar open-config`           | Ouvre le fichier de configuration dans l’éditeur par défaut.  |
| `radar open-app-dir`          | Ouvre le répertoire principal de l’application.               |
| `radar reset [--config-only]` | Réinitialise l’application.                                   |

### Exemple rapide

```bash
# Initialiser l'application avec radar exemple
radar init

# Lister les radars
radar list

# Créer un nouveau radar "mon_radar"
radar new mon_radar

# Générer le radar HTML
radar refresh mon_radar

# Visualiser le radar dans le navigateur
radar serve mon_radar
```

###Utilisation en python

```python
from tech_radar_builder import radars

# Initialiser l'application (création des dossiers/templates)
radars.init_app()

# Lister les radars
print(radars.list())

# Créer un radar
radars.new("mon_radar")

# Obtenir un objet TechRadar
radar = radars.get("mon_radar")
radar.build()

# Rafraîchir le radar
radars.refresh("mon_radar")
```
## Astuces Windows

* S’assurer que Python est dans le PATH.
* Installer avec pip install -e . ou pipx install ....
* Vérifier la commande :

```bash
radar --help

```
* Pour arrêter le serveur local : Ctrl+C dans le terminal.
* Pour créer un raccourci automatique : créer un radar.bat :

```bat
@echo off
radar serve zalando
pause
```