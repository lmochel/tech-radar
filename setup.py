from setuptools import setup, find_packages

setup(
    name="tech_radar_builder",
    version="0.1.0",
    author="Loïc Momo",
    description="Outil CLI pour générer, servir et gérer des Tech Radars depuis Excel et Markdown.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "tech_radar_builder": [
            "examples/*.md",
            "examples/*.xlsx",
            "templates/*.j2",
            "templates/*.css",
        ],
    },
    install_requires=[
        "pandas",
        "openpyxl",
        "jinja2",
        "markdown",
        "appdirs",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "watchdog>=3.0.0"
    ],
    entry_points={
        "console_scripts": [
            "radar=tech_radar_builder.cli:app",
        ],
    },
    python_requires=">=3.10",
)
