import os
from pathlib import Path
import platform

def get_default_app_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        appdata = os.getenv("APPDATA", Path.home())
        return Path(appdata) / "tech_radar"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "tech_radar"
    else:
        return Path.home() / ".config" / "tech_radar"
