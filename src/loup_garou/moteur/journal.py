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
