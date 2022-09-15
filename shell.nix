with import <nixpkgs> {};

let
  pycord = ps: ps.callPackage ./pycord.nix {
  };

in
(pkgs.python38.withPackages (ps: with ps; [
  (pycord ps)
  sqlalchemy
  requests
  python-lsp-server
])).env
