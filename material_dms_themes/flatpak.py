"""Flatpak: let sandboxed apps see the themes. A user-wide override (applies to system flatpaks too).

GTK apps read gtk-3.0/gtk-4.0 (the libadwaita look, DMS's dank-colors.css) and the themes directory (the named theme
and its adw-gtk3 base). Qt apps in the KDE runtimes have no qtengine: they use KDE's platform theme, which reads
kdeglobals (DMS's color scheme), and get the Kvantum style from QT_STYLE_OVERRIDE, which needs the Kvantum Flatpak
extension for each runtime and the theme in ~/.config/Kvantum.
"""
import configparser
import io
import subprocess

FILESYSTEMS = [
    "xdg-config/gtk-3.0:ro", "xdg-config/gtk-4.0:ro", "xdg-data/themes:ro",
    "xdg-config/kdeglobals:ro", "xdg-config/Kvantum:ro", "xdg-config/material-dms-themes:ro",
]
# set when absent: a value the user already chose is theirs. The first two stop the host's qtengine leaking in.
ENV_DEFAULT = {"QT_QPA_PLATFORMTHEME": "kde", "QT_QPA_PLATFORMTHEME_QT6": "kde"}
ENV_FORCED = {"QT_STYLE_OVERRIDE": "kvantum"}
ENV_QUICK = {"QT_QUICK_CONTROLS_STYLE": "Material",  # opt in: it applies to every QML program
             "QT_QUICK_CONTROLS_CONF": "{home}/.config/material-dms-themes/qtquickcontrols2.conf"}
EXTENSION = "org.kde.KStyle.Kvantum"


def merged(existing_text, home, quick=False):
    """The override file text with our paths and variables added; everything else in it is kept."""
    cp = configparser.RawConfigParser(delimiters=("=",))
    cp.optionxform = str
    if existing_text:
        cp.read_string(existing_text)
    for section in ("Context", "Environment"):
        if not cp.has_section(section):
            cp.add_section(section)
    have = [x for x in cp.get("Context", "filesystems", fallback="").split(";") if x]
    cp.set("Context", "filesystems", ";".join(have + [f for f in FILESYSTEMS if f not in have]))
    for k, v in ENV_DEFAULT.items():
        if not cp.has_option("Environment", k):
            cp.set("Environment", k, v)
    for k, v in {**ENV_FORCED, **(ENV_QUICK if quick else {})}.items():
        cp.set("Environment", k, v.format(home=home))
    out = io.StringIO()
    cp.write(out, space_around_delimiters=False)
    return out.getvalue()


def kde_runtime_branches():
    """Branches of the installed org.kde.Platform runtimes (the Kvantum extension must match each)."""
    out = subprocess.run(["flatpak", "list", "--runtime", "--columns=application,branch"],
                         capture_output=True, text=True, check=True).stdout
    return sorted({line.split()[1] for line in out.splitlines()
                   if line.split() and line.split()[0] == "org.kde.Platform" and len(line.split()) > 1})


def install_extensions(branches):
    for b in branches:
        subprocess.run(["flatpak", "install", "--user", "-y", "flathub", f"{EXTENSION}//{b}"], check=False)
