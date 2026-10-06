"""Statistiques sur les parties archivées (sans Streamlit)."""

from collections import Counter

from loup_garou.moteur.persistance import gagnant_partie
from loup_garou.roles import ROLES

# (libellé, nombre de joueurs maximal) ; la dernière tranche n'a pas de borne.
TRANCHES = (("5 à 8 joueurs", 8), ("9 à 12 joueurs", 12), ("13 joueurs et plus", None))


def camp_effectif(d):
    role = ROLES.get(d["role"])
    return d.get("camp_choisi") or (role.camp if role else "village")


def a_gagne(vainqueur, d):
    """Ce joueur est-il du camp vainqueur ? (le couple et le Loup Blanc gagnent à part)"""
    if vainqueur == "couple":
        return bool(d.get("amoureux"))
    if vainqueur == "loupblanc":
        return d["role"] == "loup_blanc"
    if vainqueur in ("village", "loups"):
        return camp_effectif(d) == ("village" if vainqueur == "village" else "loups")
    return False


def _tranche(nb):
    for libelle, maxi in TRANCHES:
        if maxi is None or nb <= maxi:
            return libelle


def statistiques(parties):
    """Victoires par camp, taux de victoire du village par taille de table, et fiche par rôle."""
    victoires = Counter()
    tailles = {libelle: Counter() for libelle, _ in TRANCHES}
    roles = {}
    for p in parties:
        vainqueur = gagnant_partie(p["issue"])[0]
        victoires[vainqueur] += 1
        tailles[_tranche(len(p["joueurs"]))][vainqueur] += 1
        for d in p["joueurs"].values():
            fiche = roles.setdefault(d["role"], {"parties": 0, "victoires": 0, "survivants": 0})
            fiche["parties"] += 1
            fiche["victoires"] += a_gagne(vainqueur, d)
            fiche["survivants"] += bool(d.get("vivant"))
    return {
        "total": len(parties),
        "joueurs": sum(len(p["joueurs"]) for p in parties),
        "victoires": dict(victoires),
        "tailles": [
            (libelle, sum(c.values()), c["village"] / sum(c.values()) if c else None)
            for libelle, c in tailles.items()
        ],
        "roles": sorted(
            (
                (cle, f["parties"], f["victoires"] / f["parties"], f["survivants"] / f["parties"])
                for cle, f in roles.items() if cle in ROLES
            ),
            key=lambda r: (-r[1], r[0]),
        ),
    }
