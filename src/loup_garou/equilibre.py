"""Jauges d'équilibre d'une composition : force, information et chaos (voir docs/equilibre-roles.md).

Valeurs proposées, à ajuster après quelques parties. Pas de dépendance à Streamlit.
"""

from collections import namedtuple

from loup_garou.options import OPTIONS_DEFAUT

Notes = namedtuple("Notes", "force info chaos")
Bilan = namedtuple("Bilan", "force info chaos joueurs")

# force : positif = avantage village, négatif = avantage loups ; info et chaos : 0 à 5.
NOTES = {
    "loup": Notes(-6, 1, 0),
    "villageois": Notes(1, 0, 0),
    "voyante": Notes(7, 5, 0),  # une vision par nuit ; la cadence choisie l'ajuste (ci-dessous)
    "sorciere": Notes(3, 1, 2),
    "cupidon": Notes(-3, 0, 4),
    "chasseur": Notes(3, 0, 1),
    "salvateur": Notes(3, 0, 1),
    "renard": Notes(3, 3, 0),
    "enfant_sauvage": Notes(-1, 0, 3),
    "voleur": Notes(-2, 0, 4),
    "loup_blanc": Notes(-5, 1, 4),
    "chien_loup": Notes(0, 0, 2),
    "louveteau": Notes(-8, 1, 2),
    "soeur": Notes(2, 2, 0),  # par carte : les deux sœurs pèsent donc +4
    "frere": Notes(2, 2, 0),  # par carte : les trois frères pèsent donc +6
    "servante": Notes(2, 0, 3),
    "juge_begue": Notes(2, 0, 3),
}

FORCE_VOYANTE = {1: 7, 2: 5, 3: 4}
FORCE_LOUP_BLANC = {1: -6, 2: -5, 3: -4}

# Demi-largeur de la jauge d'équilibre : 2 points de force par joueur (au moins 10), pour qu'un
# rôle pèse moins sur le curseur à une grande table qu'à une petite.
FORCE_PAR_JOUEUR = 2
DEMI_LARGEUR_MIN = 10
# Seuils des jauges d'information et de chaos, rapportées à la table.
SEUILS_INFO = (0.4, 0.9)    # information par joueur : faible / moyenne / forte
SEUILS_CHAOS = (0.3, 0.8)  # chaos par joueur : calme / mouvementée / imprévisible


def _option(options, cle):
    return (options or {}).get(cle, OPTIONS_DEFAUT[cle])


def bilan(composition, nb_joueurs, options=None):
    """Somme des notes de la composition (`{rôle: nombre}`, villageois compris), options incluses."""
    force = info = chaos = 0
    for cle, n in composition.items():
        notes = NOTES[cle]
        force += notes.force * n
        info += notes.info * n
        chaos += notes.chaos * n

    if composition.get("voyante"):
        force += composition["voyante"] * (FORCE_VOYANTE[_option(options, "cadence_voyante")] - NOTES["voyante"].force)
    if composition.get("loup_blanc"):
        force += composition["loup_blanc"] * (
            FORCE_LOUP_BLANC[_option(options, "cadence_loup_blanc")] - NOTES["loup_blanc"].force
        )
    if composition.get("sorciere"):
        potions_mort = _option(options, "potions_mort")
        force += composition["sorciere"] * (_option(options, "potions_sorciere") - 1 + potions_mort)
        if potions_mort:
            chaos += 1
    if _option(options, "couple_hasard"):
        chaos += 2
    if _option(options, "trouple") and (composition.get("cupidon") or _option(options, "couple_hasard")):
        chaos += 3
    if not _option(options, "maire_depart"):
        force -= 2

    return Bilan(force, info, chaos, nb_joueurs)


def position_equilibre(b):
    """Position du curseur entre 0 (avantage loups) et 100 (avantage village), 50 = équilibre."""
    demi = max(DEMI_LARGEUR_MIN, FORCE_PAR_JOUEUR * b.joueurs)
    return 50 + max(-demi, min(demi, b.force)) / demi * 50


def _niveau(total, joueurs, seuils, libelles):
    par_joueur = total / max(joueurs, 1)
    return libelles[sum(par_joueur >= s for s in seuils)]


def niveau_info(b):
    return _niveau(b.info, b.joueurs, SEUILS_INFO, ("Faible", "Moyenne", "Forte"))


def niveau_chaos(b):
    return _niveau(b.chaos, b.joueurs, SEUILS_CHAOS, ("Calme", "Mouvementée", "Imprévisible"))
