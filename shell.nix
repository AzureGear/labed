{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  packages = with pkgs; [
    python311
    poetry
    direnv
    # Нативные библиотеки для wheel пакетов rasterio, shapely, Pillow
    pkg-config
    zlib
    libjpeg
    gdal
    geos
    proj
    # PyQt5 (pip wheel): libqxcb нуждается в полном XCB + xkbcommon + dbus (у Nix'а же нет глобального /usr/lib)
    glib
    fontconfig
    freetype
    dbus
    libxkbcommon
    xorg.libX11
    xorg.libXext
    xorg.libXcursor
    xorg.libxcb
    xorg.libXrender
    xorg.libXau
    xorg.libXdmcp
    xorg.xcbutilwm
    xorg.xcbutilimage
    xorg.xcbutilkeysyms
    xorg.xcbutilrenderutil
    libglvnd
  ];

  shellHook = ''
    export GDAL_CONFIG="${pkgs.gdal}/bin/gdal-config"
    export PROJ_LIB="${pkgs.proj}/share/proj"
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
      pkgs.gdal
      pkgs.geos
      pkgs.proj
      pkgs.zlib
      pkgs.stdenv.cc.cc.lib
      pkgs.glib
      pkgs.fontconfig
      pkgs.freetype
      pkgs.dbus
      pkgs.libxkbcommon
      pkgs.xorg.libX11
      pkgs.xorg.libXext
      pkgs.xorg.libXcursor
      pkgs.xorg.libxcb
      pkgs.xorg.libXrender
      pkgs.xorg.libXau
      pkgs.xorg.libXdmcp
      pkgs.xorg.xcbutilwm
      pkgs.xorg.xcbutilimage
      pkgs.xorg.xcbutilkeysyms
      pkgs.xorg.xcbutilrenderutil
      pkgs.libglvnd
    ]}:''$LD_LIBRARY_PATH"
    # Pip PyQt5 Wayland plugins often fail on Nix; xcb uses XWayland (inherits QT_QPA_PLATFORM=wayland from the desktop).
    case "''${QT_QPA_PLATFORM-}" in
      wayland|wayland-egl) export QT_QPA_PLATFORM=xcb ;;
    esac
  '';
}
