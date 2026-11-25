# material-dms-themes

The look of [DankMaterialShell](https://github.com/AvengeMedia/DankMaterialShell) for GTK 3, GTK 4 / libadwaita and
Qt (Kvantum): the same shapes, sizes and state layers. **Colors are DMS's.** DMS already writes `dank-colors.css`,
the KDE color schemes (`DankMatugen*.colors`) and the qt5ct/qt6ct palettes on every theme change; this project does
not redo that. It adds only what DMS does not provide: the shapes.

| Target | What this adds | Colors from |
|---|---|---|
| GTK 3 and GTK 4 | the named theme `MaterialDMS` (`~/.local/share/themes/`): adw-gtk3 / Adwaita as the base, then DMS's `dank-colors.css`, then the look. Static; select it in your GTK settings. | DMS's `dank-colors.css` (named colors; tones DMS doesn't name are mixes of those it does) |
| libadwaita apps | libadwaita ignores named themes, so `install` also adds `material-dms.css` and an import to `~/.config/gtk-4.0/gtk.css` (DMS's import is kept) | the same |
| Qt / KDE | a Kvantum theme, `MaterialDMS`, regenerated when DMS's palette changes (an SVG cannot use named colors) | DMS's `~/.cache/dms/dms-colors.json` |
| qtengine | nothing: DMS writes `~/.config/qtengine/config.json` (color scheme, fonts, icons, style). The only thing needed from it is `theme.style = "kvantum"`, to use our theme (DMS currently writes `Fusion`). | DMS |
| QML apps | a Material Quick Controls conf in DMS's colors, `~/.config/material-dms-themes/qtquickcontrols2.conf`; set `QT_QUICK_CONTROLS_STYLE=Material` and `QT_QUICK_CONTROLS_CONF` to it | DMS's `dms-colors.json` |

The look: pill buttons (tonal, filled, text), 4 px filled text fields with a 2 px primary ring on focus, DMS's 52x32
switch, a 24 px slider track with a 4 px handle, 12 px rows and cards, 16 px popovers; hover and press are the text color at 8% and 10%.

## Use

    material-dms-themes install     # GTK theme + libadwaita override + Kvantum theme, once
    material-dms-themes watch       # keep the Kvantum theme in step with DMS (the GTK look needs nothing)

`install --only gtk` or `--only kvantum` limits it. Then select `MaterialDMS` as the GTK theme (settings.ini `gtk-theme-name`, or gsettings) and Kvantum for Qt. Files that are symlinks are skipped with a message.

## Requires

- **Kvantum** (the Qt style plugin, Qt 6 and Qt 5 builds): the Qt theme is a Kvantum theme. It is the way to give Qt widgets their own shapes; qtengine, qt6ct and `QT_STYLE_OVERRIDE` only select it. `install` warns if the plugin is not found.
- **adw-gtk3**: the base of the GTK 3 theme (GTK 4 builds on its built-in Adwaita).
- **DMS** with dynamic theming on: it writes `dank-colors.css` and `~/.cache/dms/dms-colors.json`.

The Nix package lists the first two as `propagatedUserEnvPkgs` and the home-manager module installs them.

Without qtengine, select Kvantum with `QT_STYLE_OVERRIDE=kvantum`. With qtengine, its `style` decides (see above).

## Flatpak

On NixOS the system module does all of this by itself, with no CLI step: `nixosModules.default` with `programs.material-dms-themes.enable = true`
installs adw-gtk3 and the Kvantum Qt 5/6 plugins on the host and, whenever `services.flatpak.enable` is on, runs a oneshot service
that installs the `org.gtk.Gtk3theme.adw-gtk3` (and `-dark`) extensions and `org.kde.KStyle.Kvantum` for each installed
KDE runtime branch (system installation, after nix-flatpak's install), and sets a system-wide override with the paths and
`QT_STYLE_OVERRIDE=kvantum` below. Elsewhere, the CLI does the same per user:

    material-dms-themes flatpak                       # merge the override into ~/.local/share/flatpak/overrides/global
    material-dms-themes flatpak --install-extensions  # also install the Kvantum extension for each KDE runtime

The override exposes `gtk-3.0`, `gtk-4.0`, `themes`, `kdeglobals`, `Kvantum` and `material-dms-themes` read-only, and sets
the KDE platform theme (runtimes have no qtengine) and `QT_STYLE_OVERRIDE=kvantum`; `--quick-controls` adds the Quick Controls variables (off by default: they apply to every QML program). Existing
entries are kept and a `QT_QPA_PLATFORMTHEME` you set yourself is not replaced. `--print` shows it without writing; a
symlinked override (home-manager's) is skipped. Kvantum in the sandbox needs `org.kde.KStyle.Kvantum` for each
KDE runtime branch (`flatpak list --runtime`). Not yet tested with a real Flatpak app.

### NixOS

```nix
imports = [ inputs.material-dms-themes.nixosModules.default ];
programs.material-dms-themes.enable = true;   # .flatpak.enable follows services.flatpak.enable
```

This is the system side (host packages, Flatpak). The per-user look is the home-manager module below.

### home-manager

```nix
inputs.material-dms-themes.url = "github:randalthor17/material-dms-themes";
imports = [ inputs.material-dms-themes.homeManagerModules.default ];
programs.material-dms-themes.enable = true;   # .gtk.enable / .kvantum.enable to pick one
```

This makes `gtk.css` a managed file (DMS only needs to write `dank-colors.css`), sets adw-gtk3, installs Kvantum and
runs `watch` as a user service. For setups where DMS owns `gtk.css`, set `gtk.enable = false` and `gtk.activate = true`: no GTK file is managed, and `install --only gtk` runs at activation. Session-wide `QT_QUICK_CONTROLS_STYLE=Material` is opt-in (`quickControls.enable`), since it also reaches DMS's own QML. `programs.material-dms-themes.flatpak.enable = true` also writes the Flatpak override (off by default, since only one module can own that file; otherwise merge `programs.material-dms-themes.flatpak.override` into yours).

## Development

    nix develop
    tools/render.sh out.png ~/cfg -- python3 tools/preview_gtk4.py     # headless screenshot in a private Xvfb display

`RENDER_CLICKS="x:y:name ..."` clicks through tabs. For Kvantum, run `kvantumpreview` with `QT_STYLE_OVERRIDE=kvantum`
and `XDG_CONFIG_HOME` set to a directory made by `install --config-dir DIR`.

Layout: `material_dms_themes/data/` (`dank-roles.css`, `gtk{3,4}.css`), `gtk.py`, `kvantum.py` (SVG and kvconfig from
the palette), `cli.py`, `nix/`.

## Status

0.1.0. Checked in headless renders, dark palette: GTK 3, GTK 4 (libadwaita 1.10) and Kvantum. Not looked at yet: light
mode, Qt 5, Dolphin / System Settings, Flatpak apps, the home-manager module in a real config.
