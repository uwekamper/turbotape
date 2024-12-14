{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {

  packages = [
    pkgs.python3
    pkgs.poetry
    pkgs.git
  ];

  shellHook = ''
    poetry install
    source .venv/bin/activate
  '';
}
