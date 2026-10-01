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
}

FORCE_VOYANTE = {1: 7, 2: 5, 3: 4}
FORCE_LOUP_BLANC = {1: -6, 2: -5, 3: -4}

# Seuils de la jauge d'équilibre (somme des forces) et des jauges rapportées à la table.
SEUIL_EQUILIBRE = 3
SEUIL_NET = 10
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


def niveau_equilibre(force):
    """(libellé, camp favorisé : "village", "loups" ou None)."""
    if abs(force) <= SEUIL_EQUILIBRE:
        return "Équilibrée", None
    camp = "village" if force > 0 else "loups"
    ampleur = "Net avantage" if abs(force) >= SEUIL_NET else "Léger avantage"
    return f"{ampleur} {'au village' if camp == 'village' else 'aux loups'}", camp


def _niveau(total, joueurs, seuils, libelles):
    par_joueur = total / max(joueurs, 1)
    return libelles[sum(par_joueur >= s for s in seuils)]


def niveau_info(b):
    return _niveau(b.info, b.joueurs, SEUILS_INFO, ("Faible", "Moyenne", "Forte"))


def niveau_chaos(b):
    return _niveau(b.chaos, b.joueurs, SEUILS_CHAOS, ("Calme", "Mouvementée", "Imprévisible"))
