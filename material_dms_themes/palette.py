"""Read the palette DMS writes (~/.cache/dms/dms-colors.json): Material 3 roles for dark and light."""
import json
import os
from pathlib import Path

REQUIRED = [
    "primary", "on_primary", "primary_container", "on_primary_container", "secondary", "secondary_container",
    "on_secondary_container", "tertiary", "error", "on_error", "error_container", "on_error_container", "surface",
    "on_surface", "on_surface_variant", "surface_dim", "surface_bright", "surface_container_lowest",
    "surface_container_low", "surface_container", "surface_container_high", "surface_container_highest", "outline",
    "outline_variant", "inverse_surface", "inverse_on_surface", "inverse_primary", "scrim", "shadow",
]


def default_path():
    cache = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(cache) / "dms" / "dms-colors.json"


class Palette:
    """roles["primary"] -> "#rrggbb" for the chosen mode."""

    def __init__(self, roles, mode):
        self.roles = roles
        self.mode = mode

    def __getitem__(self, role):
        return self.roles[role]

    @property
    def dark(self):
        return self.mode == "dark"


def load(path=None, mode="auto"):
    path = Path(path) if path else default_path()
    data = json.loads(path.read_text())
    if mode == "auto":
        mode = data.get("mode", "dark")
    if mode not in ("dark", "light"):
        raise ValueError(f"mode must be dark, light or auto, not {mode!r}")
    roles = data["colors"][mode]
    missing = [r for r in REQUIRED if r not in roles]
    if missing:
        raise ValueError(f"{path}: missing roles {', '.join(missing)}")
    return Palette(roles, mode)


def rgb(hexcolor):
    h = hexcolor.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    """a toward b by t (0..1), as #rrggbb."""
    ra, rb = rgb(a), rgb(b)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))
