{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "sdn-project-env";

  packages = [
    pkgs.python3
    pkgs.poetry
  ];

  # This specifically fixes the "libstdc++.so.6: cannot open shared object file" error
  # by adding the C++ standard library to the linker path.
  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.glib
    ]}:$LD_LIBRARY_PATH"
    
    echo "Environment loaded. LD_LIBRARY_PATH set for NumPy."
  '';
}

