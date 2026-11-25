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
  quick = lib.optionalAttrs cfg.quickControls.enable {
    QT_QUICK_CONTROLS_STYLE = "Material";
    QT_QUICK_CONTROLS_CONF = "${config.xdg.configHome}/material-dms-themes/qtquickcontrols2.conf";
  };
  wrapMaterial = pkg: pkgs.symlinkJoin {
    name = "${pkg.pname or pkg.name}-material-dms";
    paths = [ pkg ];
    nativeBuildInputs = [ pkgs.makeWrapper ];
    postBuild = ''
      for bin in $out/bin/*; do
        wrapProgram "$bin" --set QT_QUICK_CONTROLS_STYLE Material \
          --set QT_QUICK_CONTROLS_CONF "${config.xdg.configHome}/material-dms-themes/qtquickcontrols2.conf"
      done
      # desktop entries are symlinks to the originals, whose Exec names the unwrapped binary: rewrite them
      if [ -d $out/share/applications ]; then
        for f in $out/share/applications/*.desktop; do
          orig=$(readlink -f "$f"); rm "$f"
          sed "s|${pkg}/bin|$out/bin|g" "$orig" > "$f"
        done
      fi
    '';
  };
  # the named GTK theme, importing DMS's dank-colors.css by absolute path
  theme = pkgs.runCommand "material-dms-gtk-theme" { } "${cfg.package}/bin/material-dms-themes build-theme $out --config-dir ${config.xdg.configHome} --adw-gtk3 ${pkgs.adw-gtk3}/share/themes/adw-gtk3";
in {
  options.programs.material-dms-themes = {
    enable = lib.mkEnableOption "the DankMaterialShell look for GTK and Qt apps, on DMS's colors";
    package = lib.mkOption { type = lib.types.package; default = pkg; };
    gtk.enable = lib.mkOption { type = lib.types.bool; default = true; description = "Install the GTK 3/4 stylesheet and set adw-gtk3 for GTK 3. gtk.css becomes a managed file; DMS only needs to write dank-colors.css."; };
    gtk.activate = lib.mkOption { type = lib.types.bool; default = false; description = "For setups where DMS owns gtk.css: do not manage any GTK file; at activation run `material-dms-themes install --only gtk`, which adds the import to gtk.css only if missing and writes the MaterialDMS theme as real files. Use with gtk.enable = false."; };
    quickControls.apps = lib.mkOption { type = lib.types.listOf lib.types.package; default = []; example = lib.literalExpression "[ pkgs.kdePackages.kdeconnect-kde ]"; description = "Programs to run with the Material Quick Controls style (and our conf in DMS's colors) without setting it for everything: each is wrapped, its binaries and its desktop entries. Takes precedence over the same package in the system profile. DBus- and systemd-started instances of a program bypass the wrapper."; };
    quickControls.enable = lib.mkOption { type = lib.types.bool; default = false; description = "Set QT_QUICK_CONTROLS_STYLE=Material (and the conf in DMS's colors) for every session and Flatpak app. Off by default: it applies to all QML programs, DMS's own included."; };
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
        } // quick;
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

    (lib.mkIf cfg.gtk.activate {
      home.packages = [ pkgs.adw-gtk3 ];
      home.activation.materialDmsGtk = lib.hm.dag.entryAfter [ "writeBoundary" ] ''
        run ${cfg.package}/bin/material-dms-themes install --only gtk
      '';
    })

    (lib.mkIf cfg.flatpak.enable {
      xdg.dataFile."flatpak/overrides/global".text = lib.generators.toINI { } {
        Context.filesystems = lib.concatStringsSep ";" cfg.flatpak.override.Context.filesystems;
        inherit (cfg.flatpak.override) Environment;
      };
    })

    (lib.mkIf (cfg.quickControls.apps != [ ]) {
      home.packages = map (p: lib.hiPrio (wrapMaterial p)) cfg.quickControls.apps;
    })

    (lib.mkIf cfg.kvantum.enable {
      home.packages = [ pkgs.qt6Packages.qtstyleplugin-kvantum pkgs.libsForQt5.qtstyleplugin-kvantum ];
      home.sessionVariables = quick;
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
