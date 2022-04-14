with import <nixpkgs> {};

(pkgs.python38.withPackages (ps: with ps; [
  discordpy
  python-lsp-server
])).env
