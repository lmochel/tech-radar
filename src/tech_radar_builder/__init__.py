"""
tech_radar_builder
==================

Un outil pour construire et gérer des Tech Radars depuis des fichiers Excel et Markdown.
"""

from tech_radar_builder.core.radar_library import RadarLibrary

# Instance unique (type singleton léger)
radars = RadarLibrary()

__all__ = ["radars", "RadarLibrary"]
__version__ = "0.1.0"
