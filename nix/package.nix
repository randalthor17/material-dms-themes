{ python3Packages, qt6Packages, libsForQt5, adw-gtk3 }:
python3Packages.buildPythonApplication {
  pname = "material-dms-themes";
  version = "0.1.0";
  pyproject = true;
  src = ../.;
  build-system = [ python3Packages.setuptools ];
  # What the themes need at run time. Kvantum is a Qt style plugin (found through QT_PLUGIN_PATH, so it has to be in
  # the user's or system's environment, not just in this program's closure) and adw-gtk3 is GTK 3's base theme.
  # `nix profile install` and nix-env install these beside the program; the home-manager module does the same.
  propagatedUserEnvPkgs = [ qt6Packages.qtstyleplugin-kvantum libsForQt5.qtstyleplugin-kvantum adw-gtk3 ];
  meta = {
    description = "GTK and Kvantum themes drawn like DankMaterialShell";
    mainProgram = "material-dms-themes";
  };
}
