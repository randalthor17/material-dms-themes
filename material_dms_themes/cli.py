"""material-dms-themes: the GTK look on DMS's colors, and a Kvantum theme in DMS's palette."""
import argparse
import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

from . import __version__, flatpak, gtk, kvantum, quickcontrols
from .palette import default_path, load

KV_NAME = "MaterialDMS"


def write(path: Path, text: str):
    """Atomic write; leaves a symlink (home-manager's) alone and says so. True if the file changed."""
    if path.is_symlink():
        print(f"skipped {path}: it is a symlink (managed elsewhere)", file=sys.stderr)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() == text:
        return False
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)
    return True


def set_kvantum_theme(cfg: Path):
    """Select the theme in Kvantum's own config, keeping its other keys."""
    path = cfg / "Kvantum" / "kvantum.kvconfig"
    if path.is_symlink():
        return
    lines = path.read_text().splitlines() if path.exists() else []
    out, in_general, done = [], False, False
    for line in lines:
        s = line.strip()
        if s.startswith("["):
            if in_general and not done:
                out.append(f"theme={KV_NAME}")
                done = True
            in_general = s == "[General]"
        elif in_general and s.split("=")[0].strip() == "theme":
            line, done = f"theme={KV_NAME}", True
        out.append(line)
    if not done:
        out += ([""] if out else []) + (["[General]"] if not in_general else []) + [f"theme={KV_NAME}"]
    write(path, "\n".join(out) + "\n")


def install_gtk(cfg: Path):
    """material-dms.css beside DMS's dank-colors.css, imported from gtk.css (DMS's import is kept)."""
    changed = []
    for version, d in ((3, "gtk-3.0"), (4, "gtk-4.0")):
        base = cfg / d
        if write(base / "material-dms.css", gtk.material_css(version)):
            changed.append(base / "material-dms.css")
        css = base / "gtk.css"
        new = gtk.with_import(css.read_text() if css.exists() else "")
        if new is not None and write(css, new):
            changed.append(css)
    return changed


def build_theme(dest: Path, config_dir: Path, adw_gtk3=None):
    """The named GTK theme (index.theme, gtk-3.0, gtk-4.0) in dest. Returns the files that changed."""
    changed = [dest / "index.theme"] if write(dest / "index.theme", gtk.INDEX) else []
    for v in (3, 4):
        f = dest / f"gtk-{v}.0" / "gtk.css"
        if write(f, gtk.theme_css(v, config_dir, adw_gtk3)):
            changed.append(f)
    return changed


def write_kvantum(cfg: Path, colors, mode):
    p = load(colors, mode)
    kv = cfg / "Kvantum" / KV_NAME
    changed = [kv / n for n, t in ((f"{KV_NAME}.kvconfig", kvantum.config(p)),
                                   (f"{KV_NAME}.svg", kvantum.build(p).text())) if write(kv / n, t)]
    set_kvantum_theme(cfg)
    return p, changed


def write_qt(cfg: Path, colors, mode):
    """The Kvantum theme and the Quick Controls conf, from DMS's palette. qtengine's config is DMS's to write."""
    p, changed = write_kvantum(cfg, colors, mode)
    conf = cfg / "material-dms-themes" / "qtquickcontrols2.conf"
    if write(conf, quickcontrols.conf(p)):
        changed.append(conf)
    return p, changed


def config_dir(args):
    return Path(args.config_dir or os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")


def kvantum_installed():
    """True if Kvantum's Qt style plugin is on the Qt plugin path or in a system data location."""
    dirs = (os.environ.get("QT_PLUGIN_PATH") or "").split(":") + [str(Path.home() / ".nix-profile/lib/qt-6/plugins"), "/run/current-system/sw/lib/qt-6/plugins", "/usr/lib/qt6/plugins", "/usr/lib64/qt6/plugins", "/usr/lib/qt/plugins", "/usr/lib/x86_64-linux-gnu/qt6/plugins"]
    return any((Path(d) / "styles" / "libkvantum.so").exists() for d in dirs if d)


def install(args):
    cfg = config_dir(args)
    targets = set(args.only.split(",")) if args.only else {"gtk", "kvantum"}
    n = 0
    if "gtk" in targets:
        n += len(install_gtk(cfg))  # libadwaita ignores named themes, so it gets the look from gtk.css
        data = Path(args.data_dir or os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
        adw = Path(args.adw_gtk3) if args.adw_gtk3 else gtk.find_adw_gtk3()
        if adw is None:
            print("adw-gtk3 not found: the GTK 3 theme will lack its base (install adw-gtk3)", file=sys.stderr)
        n += len(build_theme(data / "themes" / gtk.THEME_NAME, cfg.resolve(), adw))
    if "kvantum" in targets:
        p, changed = write_qt(cfg, args.colors, args.mode)
        if not kvantum_installed():
            print("Kvantum's Qt style plugin was not found: install Kvantum (qt6 and qt5 packages) for Qt apps to use the theme", file=sys.stderr)
        n += len(changed)
    print(f"wrote {n} file(s)" if n else "already up to date")
    return 0


def flatpak_cmd(args):
    home = str(Path.home())
    path = Path(args.data_dir or os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "flatpak" / "overrides" / "global"
    text = flatpak.merged(path.read_text() if path.exists() else "", home)
    if args.print:
        print(text, end="")
    else:
        print(f"wrote {path}" if write(path, text) else f"{path} is up to date or managed elsewhere")
    try:
        branches = flatpak.kde_runtime_branches()
    except (FileNotFoundError, subprocess.CalledProcessError):
        branches = []
    if args.install_extensions:
        flatpak.install_extensions(branches)
    elif branches:
        print("Kvantum for Qt apps in Flatpak needs its extension for each KDE runtime; run again with --install-extensions, or:")
        for b in branches:
            print(f"  flatpak install --user flathub {flatpak.EXTENSION}//{b}")
    return 0


def watch(args):
    """Rewrite the Kvantum theme when DMS's palette changes (the GTK look follows DMS's colors by itself)."""
    cfg = config_dir(args)
    path = Path(args.colors) if args.colors else default_path()
    last = None
    while True:
        try:
            stamp = path.stat().st_mtime_ns
        except FileNotFoundError:
            stamp = None
        if stamp is not None and stamp != last:
            last = stamp
            time.sleep(.3)  # DMS writes the file in a burst
            try:
                write_qt(cfg, args.colors, args.mode)
            except Exception as e:  # keep watching; the next palette may be fine
                print(f"error: {e}", file=sys.stderr)
        time.sleep(1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="material-dms-themes", description=__doc__)
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    fp = sub.add_parser("flatpak", help="let Flatpak apps see the themes (user-wide override)")
    fp.add_argument("--data-dir", help="default ~/.local/share")
    fp.add_argument("--print", action="store_true", help="print the override instead of writing it")
    fp.add_argument("--install-extensions", action="store_true", help="install the Kvantum extension for each KDE runtime")
    fp.set_defaults(fn=flatpak_cmd)
    pg = sub.add_parser("print-gtk", help="print material-dms.css for GTK 3 or 4")
    pg.add_argument("version", type=int, choices=(3, 4))
    pg.set_defaults(fn=lambda a: print(gtk.material_css(a.version), end="") or 0)
    bt = sub.add_parser("build-theme", help="write the named GTK theme to DEST (for packaging)")
    bt.add_argument("dest", type=Path)
    bt.add_argument("--config-dir", type=Path, required=True, help="where DMS writes gtk-N.0/dank-colors.css")
    bt.add_argument("--adw-gtk3", type=Path)
    bt.set_defaults(fn=lambda a: print("\n".join(map(str, build_theme(a.dest, a.config_dir, a.adw_gtk3)))) or 0)
    for name, fn, helptext in (("install", install, "write the GTK look and the Kvantum theme once"),
                               ("watch", watch, "rewrite the Kvantum theme when DMS's palette changes")):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("--colors", help="DMS's palette for Kvantum (default ~/.cache/dms/dms-colors.json)")
        sp.add_argument("--mode", default="auto", choices=("auto", "dark", "light"))
        sp.add_argument("--config-dir", help="default ~/.config")
        sp.add_argument("--data-dir", help="default ~/.local/share")
        sp.add_argument("--adw-gtk3", help="adw-gtk3 theme directory (default: found in the XDG data dirs)")
        if name == "install":
            sp.add_argument("--only", help="comma list of: gtk, kvantum")
        sp.set_defaults(fn=fn)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except FileNotFoundError as e:
        print(f"error: {e.filename} not found (is DMS running with dynamic theming?)", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
