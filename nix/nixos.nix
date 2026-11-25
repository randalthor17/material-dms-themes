# NixOS module: the system parts. With Flatpak enabled it also installs what sandboxed apps need and exposes the themes:
#  - the adw-gtk3 GTK theme extensions (org.gtk.Gtk3theme.adw-gtk3, -dark) and, for each installed KDE runtime, the
#    Kvantum extension (org.kde.KStyle.Kvantum//<runtime branch>), by a oneshot service after the flatpaks are installed
#  - a system-wide Flatpak override (flatpak override --system): the GTK, Kvantum and theme directories read-only and
#    the style variables, the same as `material-dms-themes flatpak` writes per user
# On the host: adw-gtk3 and the Kvantum Qt 5 and Qt 6 plugins. The user-side look is the home-manager module.
self: { config, lib, pkgs, ... }:
let
  cfg = config.programs.material-dms-themes;
  flatpak = "${pkgs.flatpak}/bin/flatpak";
  filesystems = [ "xdg-config/gtk-3.0:ro" "xdg-config/gtk-4.0:ro" "xdg-data/themes:ro" "xdg-config/kdeglobals:ro" "xdg-config/Kvantum:ro" "xdg-config/material-dms-themes:ro" ];
  script = pkgs.writeShellScript "material-dms-flatpak" ''
    set -u
    have() { ${flatpak} info --system "$1" >/dev/null 2>&1; }
    install() { have "$1" || ${flatpak} install --system --noninteractive flathub "$1" || echo "could not install $1" >&2; }

    install org.gtk.Gtk3theme.adw-gtk3
    install org.gtk.Gtk3theme.adw-gtk3-dark
    for branch in $(${flatpak} list --system --runtime --columns=application,branch \
        | ${pkgs.gawk}/bin/awk '$1 == "org.kde.Platform" { print $2 }' | sort -u); do
      install "org.kde.KStyle.Kvantum//$branch"
    done

    ${flatpak} override --system ${lib.concatMapStringsSep " " (f: "--filesystem=${f}") filesystems} \
      --env=QT_STYLE_OVERRIDE=kvantum
  '';
in {
  options.programs.material-dms-themes = {
    enable = lib.mkEnableOption "the system side of material-dms-themes (adw-gtk3, Kvantum, Flatpak)";
    flatpak.enable = lib.mkOption {
      type = lib.types.bool;
      default = config.services.flatpak.enable;
      defaultText = lib.literalExpression "config.services.flatpak.enable";
      description = "Install the Flatpak theme extensions and set the system-wide override. On whenever Flatpak is.";
    };
  };

  config = lib.mkIf cfg.enable (lib.mkMerge [
    {
      environment.systemPackages = [ pkgs.adw-gtk3 pkgs.qt6Packages.qtstyleplugin-kvantum pkgs.libsForQt5.qtstyleplugin-kvantum ];
    }
    (lib.mkIf cfg.flatpak.enable {
      systemd.services.material-dms-flatpak = {
        description = "Flatpak theme extensions and override for material-dms-themes";
        wantedBy = [ "multi-user.target" ];
        wants = [ "network-online.target" ];
        after = [ "network-online.target" "flatpak-managed-install.service" ];
        serviceConfig = { Type = "oneshot"; RemainAfterExit = true; ExecStart = script; };
        restartTriggers = [ script ];
      };
    })
  ]);
}
