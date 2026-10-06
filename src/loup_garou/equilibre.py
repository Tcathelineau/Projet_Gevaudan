"""Jauges d'équilibre d'une composition : chance de victoire du village, information et chaos.

Les coefficients viennent de `assets/equilibre.json`, produit par `outils/simuler_equilibre.py` (des milliers de
parties jouées par des joueurs automatiques avec le vrai moteur ; méthode et limites dans docs/equilibre-roles.md).
Pas de dépendance à Streamlit.
"""

import json
import math
from collections import namedtuple
from pathlib import Path

from loup_garou.options import OPTIONS_DEFAUT

Bilan = namedtuple("Bilan", "chance info chaos joueurs")

DONNEES = json.loads((Path(__file__).resolve().parent / "assets" / "equilibre.json").read_text(encoding="utf-8"))
MODELE = DONNEES["modele"]
# clé de rôle -> {impact_pts, info, chaos, marge_pts} ; le villageois est la référence (tout à zéro)
ROLES_NOTES = {"villageois": {"impact_pts": 0.0, "info": 0, "chaos": 0, "marge_pts": 0.0}, **DONNEES["roles"]}
EFFETS_OPTIONS = DONNEES["options"]

# Niveaux des jauges d'information et de chaos : valeur moyenne par joueur (échelle 0-100 par carte).
SEUILS_INFO = (4, 8)
SEUILS_CHAOS = (7, 13)
# Valeur par joueur qui remplit entièrement la barre.
MAX_INFO = 14
MAX_CHAOS = 24


def _option(options, cle):
    return (options or {}).get(cle, OPTIONS_DEFAUT[cle])


def _ajustement_options(composition, options):
    """Somme des effets (en log-cotes) des options sur la victoire du village."""
    total = 0.0
    if composition.get("voyante"):
        total += EFFETS_OPTIONS["cadence_voyante"].get(str(_option(options, "cadence_voyante")), 0.0)
    if composition.get("loup_blanc"):
        total += EFFETS_OPTIONS["cadence_loup_blanc"].get(str(_option(options, "cadence_loup_blanc")), 0.0)
    if composition.get("sorciere"):
        total += EFFETS_OPTIONS["potions_sorciere"] * (_option(options, "potions_sorciere") - 1)
        total += EFFETS_OPTIONS["potions_mort"] * _option(options, "potions_mort")
    if not _option(options, "maire_depart"):
        total += EFFETS_OPTIONS["maire_depart_faux"]
    if _option(options, "couple_hasard"):
        total += EFFETS_OPTIONS["couple_hasard"]
        if _option(options, "trouple"):
            total += EFFETS_OPTIONS["trouple"]
    return total


def bilan(composition, nb_joueurs, options=None):
    """Chance de victoire du village (0 à 1), information et chaos totaux de la composition (`{rôle: cartes}`)."""
    x = nb_joueurs / 10
    cotes = MODELE["intercept"] + MODELE["joueurs"] * x + MODELE["joueurs2"] * x * x
    info = chaos = 0
    for cle, n in composition.items():
        cotes += MODELE["roles"].get(cle, 0.0) * n
        notes = ROLES_NOTES.get(cle, {})
        info += notes.get("info", 0) * n
        chaos += notes.get("chaos", 0) * n
    cotes += _ajustement_options(composition, options)
    return Bilan(1 / (1 + math.exp(-cotes)), info, chaos, nb_joueurs)


def position_equilibre(b):
    """Position du curseur entre 0 (avantage loups) et 100 (avantage village) : la chance de victoire du village en %."""
    return 100 * b.chance


def _niveau(total, joueurs, seuils, libelles):
    par_joueur = total / max(joueurs, 1)
    return libelles[sum(par_joueur >= s for s in seuils)]


def niveau_info(b):
    return _niveau(b.info, b.joueurs, SEUILS_INFO, ("Faible", "Moyenne", "Forte"))


def niveau_chaos(b):
    return _niveau(b.chaos, b.joueurs, SEUILS_CHAOS, ("Calme", "Mouvementée", "Imprévisible"))


def remplissage(total, joueurs, maximum):
    """Part (0 à 1) d'une barre d'information ou de chaos."""
    return min(1.0, total / max(joueurs, 1) / maximum)
