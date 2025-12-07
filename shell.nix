{ pkgs ? import <nixpkgs> {} }:
let
  python = pkgs.python311;
  pythonEnv = python.withPackages (ps: with ps; [
    fastapi
    uvicorn
    sqlalchemy
    pydantic
    pydantic-settings
    pdfminer-six
    pypdf
    python-multipart
    httpx
    pytest
  ]);
  node = pkgs.nodejs_20;
  pnpm = pkgs.nodePackages.pnpm;
in pkgs.mkShell {
  packages = [ pythonEnv node pnpm pkgs.git ];
  shellHook = ''
    export PYTHONPATH=$PWD
    echo "Dev shell ready with Python, FastAPI, pdfminer, pypdf, and pnpm."
  '';
}
