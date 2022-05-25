with import <nixpkgs> {};

(pkgs.python38.withPackages (ps: with ps; [
  discordpy
  sqlalchemy
  requests
  python-lsp-server
])).env
