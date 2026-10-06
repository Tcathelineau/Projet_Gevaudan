"""Illustrations des rôles : icônes SVG vectorielles (cf. assets/CREDITS.md) intégrées au HTML."""

from functools import lru_cache
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"


@lru_cache(maxsize=None)
def _lire(cle):
    fichier = ASSETS / "roles" / f"{cle}.svg"
    return fichier.read_text(encoding="utf-8") if fichier.exists() else ""


def svg_role(cle, classe="art", repli=""):
    """SVG en ligne de l'illustration d'un rôle (couleur = `color` du CSS), ou `repli` s'il n'y en a pas."""
    svg = _lire(cle)
    if not svg:
        return repli
    return svg.replace("<svg ", f'<svg class="{classe}" aria-hidden="true" focusable="false" ', 1).strip()
