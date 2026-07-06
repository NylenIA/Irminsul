"""Entry PyInstaller du sidecar : wrapper top-level (les imports relatifs du package
`irminsul` exigent un entry HORS package). Ne rien mettre d'autre ici."""
from irminsul.sidecar import main

if __name__ == "__main__":
    raise SystemExit(main())
