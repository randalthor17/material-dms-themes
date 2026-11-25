"""Qt Quick Controls (QML apps): the Material style in DMS's colors, through QT_QUICK_CONTROLS_CONF."""
from .palette import Palette


def conf(p: Palette):
    """qtquickcontrols2.conf from DMS's palette."""
    return "\n".join([
        "; Material DMS: generated from DMS's palette. Do not edit.",
        "[Controls]", "Style=Material", "",
        "[Material]", f"Theme={'Dark' if p.dark else 'Light'}", f"Accent={p['primary']}",
        f"Primary={p['surface_container']}", f"Background={p['surface']}", f"Foreground={p['on_surface']}", ""])
