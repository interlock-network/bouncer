with import <nixpkgs> {};

let
  pycord = ps: ps.callPackage ./pycord.nix {
  };

in
(pkgs.python39.withPackages (ps: with ps; [
  (pycord ps)
  sqlalchemy
  requests
  flask
])).env
