with import <nixpkgs> {};

(pkgs.python38.withPackages (ps: with ps; [
  discordpy
  requests
  python-lsp-server
])).env
