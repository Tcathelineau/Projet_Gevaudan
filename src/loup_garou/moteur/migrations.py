"""Mise à niveau des parties sauvegardées : une sauvegarde d'une ancienne version reste jouable.

Chaque évolution de l'état de partie qui ajoute une clé obligatoire s'accompagne d'une migration ici :
on incrémente `VERSION`, on ajoute une fonction à `MIGRATIONS`, et `load_game` s'occupe du reste.
"""

import copy
from collections import Counter

from loup_garou.options import OPTIONS_DEFAUT
from loup_garou.roles import ROLES

VERSION = 1


def _v1(s):
    """Version 1 : clés ajoutées depuis la première version de l'application (morts, composition, rôles récents...)."""
    for role in ROLES.values():
        for cle, valeur in role.etat_initial.items():
            s.setdefault(cle, copy.deepcopy(valeur))
    s["options"] = {**OPTIONS_DEFAUT, **s.get("options", {})}
    for cle, defaut in (
        ("morts", []), ("morts_tir", []), ("tirs_en_attente", []), ("retour_tir", None), ("maire", None),
        ("dernier_maire", None), ("cartes_milieu", []), ("votes_loups", []), ("amoureux", []), ("ordre_nuit", []),
        ("tour", 0), ("devoile", False), ("transfert", False), ("servante_nuit", None), ("double_victime", False),
        ("condamnes", None), ("journal", []), ("instantanes", []),
    ):
        s.setdefault(cle, copy.deepcopy(defaut))
    s.setdefault("loups", [n for n, d in s["joueurs"].items() if ROLES[d["role"]].camp == "loups"])
    # Le paquet d'origine n'a pas été gardé : on le reconstitue à partir des rôles actuels (approximation).
    if "composition" not in s:
        paquet = Counter(d["role"] for d in s["joueurs"].values()) + Counter(s["cartes_milieu"])
        s["composition"] = dict(paquet)
    for instantane in s["instantanes"]:
        _v1(instantane["etat"])


MIGRATIONS = [(1, _v1)]


def migrer(s):
    """Amène une sauvegarde à la version courante (sur place) et la renvoie."""
    for version, fonction in MIGRATIONS:
        if s.get("version", 0) < version:
            fonction(s)
            s["version"] = version
    return s
