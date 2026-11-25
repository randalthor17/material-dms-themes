{
  description = "Material themes for GTK, KDE and Kvantum, drawn like DankMaterialShell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAll = f: nixpkgs.lib.genAttrs systems (s: f nixpkgs.legacyPackages.${s});
    in {
      packages = forAll (pkgs: rec {
        material-dms-themes = pkgs.callPackage ./nix/package.nix { };
        default = material-dms-themes;
      });
      homeManagerModules.default = import ./nix/home-manager.nix self;
      nixosModules.default = import ./nix/nixos.nix self;

      # `nix develop`: the tools to render previews headlessly (tools/render.sh) and run the checks
      devShells = forAll (pkgs: {
        default = pkgs.mkShell {
          packages = [
            (pkgs.python3.withPackages (p: [ p.pygobject3 ]))
            pkgs.xvfb-run pkgs.xvfb pkgs.xauth pkgs.imagemagick pkgs.xdotool pkgs.libxml2
            pkgs.gtk4 pkgs.gtk3 pkgs.libadwaita pkgs.adw-gtk3 pkgs.gobject-introspection pkgs.adwaita-icon-theme
            pkgs.qt6Packages.qtstyleplugin-kvantum pkgs.qt6Packages.qtbase
          ];
          GI_TYPELIB_PATH = nixpkgs.lib.makeSearchPath "lib/girepository-1.0" [ pkgs.gtk4 pkgs.libadwaita pkgs.gdk-pixbuf pkgs.pango pkgs.glib pkgs.harfbuzz pkgs.graphene ];
          shellHook = ''
            export XDG_DATA_DIRS="${pkgs.adw-gtk3}/share:${pkgs.adwaita-icon-theme}/share:${pkgs.gtk4}/share/gsettings-schemas/${pkgs.gtk4.name}:$XDG_DATA_DIRS"
          '';
        };
      });
    };
}
