"""Point d'entrée PyInstaller du sidecar moteur Irminsul.

Lit une requête JSON sur stdin, écrit une réponse JSON sur stdout (cf.
irminsul.sidecar). Empaqueté en exécutable autonome → Python NON requis chez
l'utilisateur final.
"""

import sys

from irminsul.sidecar import main

if __name__ == "__main__":
    sys.exit(main())
