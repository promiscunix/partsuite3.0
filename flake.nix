{
  description = "Dev shell for PartSuite 3.0 with FastAPI + Vite tooling";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
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
        pytest
      ]);
      node = pkgs.nodejs_20;
      pnpm = pkgs.nodePackages.pnpm;
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ pythonEnv node pnpm pkgs.git ];
        shellHook = ''
          export PYTHONPATH=$PWD
          echo "Dev shell ready with Python, FastAPI, pdfminer, pypdf, and pnpm."
        '';
      };
    };
}
