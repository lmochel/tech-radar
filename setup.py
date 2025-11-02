from setuptools import setup, find_packages

setup(
    name="tech_radar_builder",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "openpyxl",
        "jinja2",
        "markdown",
        "appdirs"
    ],
    entry_points={
        "console_scripts": [
            "radar=tech_radar_builder.cli:main",
        ]
    },
    python_requires=">=3.8",
)
