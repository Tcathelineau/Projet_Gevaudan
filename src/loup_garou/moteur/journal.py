"""Journal de partie, instantanés de chronologie."""

import copy


def log(s, texte, moment=None):
    """Ajoute un événement au journal. `moment` vaut la phase courante par défaut."""
    s.setdefault("journal", []).append(
        {"jour": s["jour"], "moment": moment or s["phase"], "texte": texte}
    )


def prendre_instantane(s, genre):
    """Copie l'état de la partie au début d'une nuit ("nuit") ou à l'annonce du réveil ("jour")."""
    if genre == "nuit":
        libelle = f"🌙 Nuit {s['jour']} · début de la nuit"
    else:
        libelle = f"☀️ Jour {s['jour']} · annonce du réveil"
    cle = f"{genre}_{s['jour']}"
    instantanes = s.setdefault("instantanes", [])
    # Une étape rejouée (après un rechargement) remplace sa version précédente et toutes celles d'après.
    for i, inst in enumerate(instantanes):
        if inst["id"] == cle:
            del instantanes[i:]
            break
    etat = copy.deepcopy({k: v for k, v in s.items() if k != "instantanes"})
    instantanes.append({"id": cle, "libelle": libelle, "etat": etat})


def etapes_chronologie(s):
    """Étapes à afficher : le départ (nuit 0 et jour 0 regroupés), puis chaque nuit et chaque jour."""
    etapes = [("start", 0)]
    for j in range(1, s["jour"] + 1):
        etapes.append(("nuit", j))
        if j < s["jour"] or s["phase"] != "nuit":
            etapes.append(("jour", j))
    return etapes
