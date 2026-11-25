"""The GTK look: static CSS on top of the named colors DMS writes to dank-colors.css."""
from importlib import resources

IMPORT = '@import url("material-dms.css");'
DANK = '@import url("dank-colors.css");'


def material_css(version):
    """material-dms.css: the roles (from DMS's names), then the look. Same file for light and dark."""
    d = resources.files("material_dms_themes").joinpath("data")
    return d.joinpath("dank-roles.css").read_text() + "\n" + d.joinpath(f"gtk{version}.css").read_text()


def with_import(existing):
    """gtk.css text with our import after DMS's (added if missing); everything else is kept."""
    lines = existing.splitlines() if existing else []
    if IMPORT in lines:
        return None
    if DANK not in lines:
        lines.insert(0, DANK)
    lines.append(IMPORT)
    return "\n".join(lines) + "\n"


THEME_NAME = "MaterialDMS"
INDEX = """[Desktop Entry]
Type=X-GNOME-Metatheme
Name=MaterialDMS
Comment=DankMaterialShell's look, in DMS's colors
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=MaterialDMS
"""


def find_adw_gtk3(search=None):
    """The adw-gtk3 theme directory (GTK 3's base), looked up in the XDG data dirs; None if absent."""
    import os
    from pathlib import Path
    dirs = search or [os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local/share"), str(Path.home() / ".themes")]
    dirs += (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":")
    for d in dirs:
        for sub in ("themes/adw-gtk3", "adw-gtk3"):
            p = Path(d) / sub
            if (p / "gtk-3.0" / "gtk.css").exists():
                return p
    return None


def theme_css(version, config_dir, adw_gtk3=None):
    """gtk-N.0/gtk.css of the named theme: a base, DMS's colors (an absolute import: DMS rewrites that file), the look.
    GTK 3 builds on adw-gtk3 (the libadwaita look for GTK 3); GTK 4 on its built-in Adwaita."""
    if version == 3:
        base = f'@import url("file://{adw_gtk3}/gtk-3.0/gtk.css");\n' if adw_gtk3 else ""
    else:
        base = '@import url("resource:///org/gtk/libgtk/theme/Adwaita/gtk.css");\n'
    colors = f'@import url("file://{config_dir}/gtk-{version}.0/dank-colors.css");\n'
    return f"/* MaterialDMS */\n{base}{colors}\n{material_css(version)}"
