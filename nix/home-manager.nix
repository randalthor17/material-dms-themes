# home-manager module. DMS writes the colors (dank-colors.css, the KDE schemes, qt6ct); this adds the look on top:
# the GTK stylesheet (static, imported after DMS's colors) and a Kvantum theme that a user service keeps in step
# with DMS's palette (~/.cache/dms/dms-colors.json), since an SVG cannot use named colors.
self: { config, lib, pkgs, ... }:
let
  cfg = config.programs.material-dms-themes;
  pkg = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
  look = v: pkgs.runCommand "material-dms-gtk${toString v}.css" { } "${cfg.package}/bin/material-dms-themes print-gtk ${toString v} > $out";
  css = ''
    @import url("dank-colors.css");
    @import url("material-dms.css");
  '';
  # the named GTK theme, importing DMS's dank-colors.css by absolute path
  theme = pkgs.runCommand "material-dms-gtk-theme" { } "${cfg.package}/bin/material-dms-themes build-theme $out --config-dir ${config.xdg.configHome} --adw-gtk3 ${pkgs.adw-gtk3}/share/themes/adw-gtk3";
in {
  options.programs.material-dms-themes = {
    enable = lib.mkEnableOption "the DankMaterialShell look for GTK and Qt apps, on DMS's colors";
    package = lib.mkOption { type = lib.types.package; default = pkg; };
    gtk.enable = lib.mkOption { type = lib.types.bool; default = true; description = "Install the GTK 3/4 stylesheet and set adw-gtk3 for GTK 3. gtk.css becomes a managed file; DMS only needs to write dank-colors.css."; };
    kvantum.enable = lib.mkOption { type = lib.types.bool; default = true; description = "Install Kvantum and keep the MaterialDMS theme in step with DMS's palette."; };
    flatpak = {
      enable = lib.mkOption { type = lib.types.bool; default = false; description = "Write the user-wide Flatpak override that exposes the themes to sandboxed apps (~/.local/share/flatpak/overrides/global). Off by default: only one module can define that file, so if you already have one, merge programs.material-dms-themes.flatpak.override into it instead."; };
      override = lib.mkOption { type = lib.types.attrs; readOnly = true; description = "The override as an attrset: Context.filesystems (a list) and Environment, to merge into your own."; };
    };
    colors = lib.mkOption { type = lib.types.nullOr lib.types.str; default = null; description = "DMS's palette file for Kvantum (default ~/.cache/dms/dms-colors.json)."; };
  };

  config = lib.mkIf cfg.enable (lib.mkMerge [
    {
      home.packages = [ cfg.package ];
      programs.material-dms-themes.flatpak.override = {
        Context.filesystems = [ "xdg-config/gtk-3.0:ro" "xdg-config/gtk-4.0:ro" "xdg-data/themes:ro" "xdg-config/kdeglobals:ro" "xdg-config/Kvantum:ro" "xdg-config/material-dms-themes:ro" ];
        Environment = {
          QT_QPA_PLATFORMTHEME = "kde";
          QT_QPA_PLATFORMTHEME_QT6 = "kde";
          QT_STYLE_OVERRIDE = "kvantum";
          QT_QUICK_CONTROLS_STYLE = "Material";
          QT_QUICK_CONTROLS_CONF = "${config.xdg.configHome}/material-dms-themes/qtquickcontrols2.conf";
        };
      };
    }

    (lib.mkIf cfg.gtk.enable {
      home.packages = [ pkgs.adw-gtk3 ];
      gtk.enable = true;
      gtk.theme.name = "MaterialDMS";
      xdg.dataFile."themes/MaterialDMS".source = theme;
      xdg.configFile = {
        # libadwaita apps ignore named themes: they get the look from gtk-4.0/gtk.css
        "gtk-4.0/material-dms.css".source = look 4;
        "gtk-4.0/gtk.css".text = css;
      };
    })

    (lib.mkIf cfg.flatpak.enable {
      xdg.dataFile."flatpak/overrides/global".text = lib.generators.toINI { } {
        Context.filesystems = lib.concatStringsSep ";" cfg.flatpak.override.Context.filesystems;
        inherit (cfg.flatpak.override) Environment;
      };
    })

    (lib.mkIf cfg.kvantum.enable {
      home.packages = [ pkgs.qt6Packages.qtstyleplugin-kvantum pkgs.libsForQt5.qtstyleplugin-kvantum ];
      home.sessionVariables = {
        QT_QUICK_CONTROLS_STYLE = "Material";
        QT_QUICK_CONTROLS_CONF = "${config.xdg.configHome}/material-dms-themes/qtquickcontrols2.conf";
      };
      systemd.user.services.material-dms-themes = {
        Unit = { Description = "Material DMS Kvantum theme follows DMS's palette"; PartOf = [ "graphical-session.target" ]; After = [ "graphical-session.target" ]; };
        Service = {
          ExecStart = "${cfg.package}/bin/material-dms-themes watch" + lib.optionalString (cfg.colors != null) " --colors ${cfg.colors}";
          Restart = "on-failure";
        };
        Install.WantedBy = [ "graphical-session.target" ];
      };
    })
  ]);
}
