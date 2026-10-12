"""Contrôle CI : une PR qui modifie le code (`src/`, `tests/`) doit aussi modifier `CHANGELOG.md`.

Usage : python outils/verifier_changelog.py <branche de base>   (ex. origin/main)
Code de sortie 1 si l'entrée de journal manque.
"""

import subprocess
import sys

DOSSIERS_CODE = ("src/", "tests/")
JOURNAL = "CHANGELOG.md"


def journal_manquant(fichiers):
    """Vrai si `fichiers` (chemins modifiés par la PR) touchent le code sans toucher au journal."""
    touche_code = any(f.startswith(DOSSIERS_CODE) for f in fichiers)
    return touche_code and JOURNAL not in fichiers


def fichiers_modifies(base):
    sortie = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"], capture_output=True, text=True, check=True,
    ).stdout
    return sortie.split()


def main(base):
    if journal_manquant(fichiers_modifies(base)):
        print(f"Cette PR modifie le code sans ajouter d'entrée à {JOURNAL}. Voir CLAUDE.md "
              "(ou poser le label « sans-changelog » pour une PR purement mécanique).")
        return 1
    print("Journal des changements : OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "origin/main"))
