"""Sauvegarde de la partie en cours, préférences et archives des parties terminées.

Ce module valide, migre et met en forme ; où les données vivent (fichiers ou base) se décide dans `stockage.py`.
Une partie se repère par son `code` : le stockage en fichiers l'ignore (une seule partie), la base s'en sert.
"""

import json
from datetime import datetime

from loup_garou.config import fuseau, maintenant
from loup_garou.moteur.migrations import VERSION, migrer
from loup_garou.moteur.stockage import stockage


def multi_parties():
    """Vrai quand plusieurs parties cohabitent (base de données) : chacune se reprend alors par son code."""
    return stockage().multi_parties


def save_game(s):
    """Écrit la sauvegarde (jamais de fichier à moitié écrit : voir `stockage.py`)."""
    s["version"] = VERSION
    stockage().ecrire_partie(s.get("code"), s)


def load_game(code=None):
    """Partie sauvegardée, mise à niveau ; None s'il n'y en a pas ou si le contenu est inutilisable
    (il est alors mis de côté, `save.json.<raison>` en fichiers, au lieu de faire planter l'application).
    Avec une base, `code` est obligatoire ; avec des fichiers il filtre seulement une sauvegarde d'une autre partie."""
    base = stockage()

    def inutilisable(raison):
        base.mettre_de_cote(code, raison)
        return None

    try:
        texte = base.lire_partie(code)
        if texte is None:
            return None
        s = json.loads(texte)
    except (OSError, ValueError):
        return inutilisable("corrompue")
    if not isinstance(s, dict) or not {"joueurs", "phase", "jour"} <= s.keys():
        return inutilisable("invalide")
    if s.get("version", 0) > VERSION:
        return inutilisable("plus_recente")
    try:
        s = migrer(s)
    except (KeyError, TypeError, AttributeError):
        return inutilisable("invalide")
    if code and s.get("code") != code:
        return None
    return s


def clear_save(code=None):
    stockage().supprimer_partie(code)


def load_preferences():
    """Préférences gardées d'une session à l'autre ({} si absentes, illisibles, ou si le stockage n'en garde pas)."""
    texte = stockage().lire_reglage("preferences")
    try:
        prefs = json.loads(texte) if texte else {}
    except ValueError:
        return {}
    return prefs if isinstance(prefs, dict) else {}


def maj_preferences(**sections):
    """Met à jour une ou plusieurs sections des préférences (`son={...}`, `composition={...}`)."""
    prefs = {**load_preferences(), **sections}
    stockage().ecrire_reglage("preferences", json.dumps(prefs, indent=2, ensure_ascii=False))


def resume_sauvegarde(code=None):
    """Résumé de la partie sauvegardée pour l'écran d'accueil, ou None : (partie, texte, date)."""
    s = load_game(code)
    if s is None:
        return None
    vivants = sum(d["vivant"] for d in s["joueurs"].values())
    phases = {
        "nuit": f"Nuit {s['jour']}", "reveil": f"Réveil, jour {s['jour']}", "election_maire": f"Élection du maire, jour {s['jour']}",
        "conseil": f"Conseil, jour {s['jour']}", "tir_chasseur": f"Dernière balle, jour {s['jour']}", "fin": "Partie terminée",
    }
    modifiee = stockage().modifie_le(code)
    if modifiee is not None and modifiee.tzinfo is not None:
        modifiee = modifiee.astimezone(fuseau())
    date = modifiee.strftime("%d/%m à %H:%M") if modifiee else "date inconnue"
    return s, f"{phases.get(s['phase'], 'Partie')} · {vivants} / {len(s['joueurs'])} en vie", date


def save_joueurs(noms):
    """Retient les noms de la dernière partie pour les proposer à la suivante."""
    stockage().ecrire_reglage("joueurs", json.dumps(list(noms), ensure_ascii=False))


def load_joueurs():
    texte = stockage().lire_reglage("joueurs")
    try:
        noms = json.loads(texte) if texte else []
    except ValueError:
        return []
    return [n for n in noms if isinstance(n, str)] if isinstance(noms, list) else []


def archiver_partie(s, issue):
    """Range le journal complet de la partie terminée (une seule fois par partie)."""
    if s.get("archive"):
        return
    date = maintenant()
    donnees = {
        "date": date.isoformat(timespec="seconds"),
        "issue": issue,
        "joueurs": s["joueurs"],
        "journal": s["journal"],
    }
    s["archive"] = stockage().ajouter_archive(s.get("code"), date, json.dumps(donnees, indent=2, ensure_ascii=False))


def lister_historique(code=None):
    """Parties archivées, de la plus récente à la plus ancienne (les contenus illisibles sont ignorés).
    Avec une base, seules les archives du `code` donné sont listées."""
    parties = []
    for texte in stockage().lister_archives(code):
        try:
            p = json.loads(texte)
        except ValueError:
            continue
        if isinstance(p, dict) and {"issue", "joueurs", "journal"} <= p.keys():
            parties.append(p)
    return parties


def date_partie(p):
    try:
        return datetime.fromisoformat(p["date"]).strftime("%d/%m/%Y à %H:%M")
    except (KeyError, ValueError):
        return "date inconnue"


# Rôles qui gagnent à part : (clé de camp vainqueur, emoji, nom du rôle).
SOLITAIRES = (
    ("loupblanc", "🌕", "Loup Blanc"), ("assassin", "🔪", "Assassin"), ("pyromane", "🔥", "Pyromane"), ("ange", "😇", "Ange"),
)


def gagnant_partie(issue):
    """(clé CSS, emoji, mot-clé) du camp vainqueur d'après le message de fin."""
    if issue.startswith("Le village a gagné"):
        return "village", "🏡", "Village"
    if issue.startswith("Les loups ont gagné"):
        return "loups", "🐺", "Loups"
    if issue.startswith("Les amoureux"):
        return "couple", "💘", "Couple"
    for cle, emoji, nom in SOLITAIRES:  # « Zoé (Pyromane) l'emporte seul. », « Zoé (Ange) l'emporte : ... »
        if f"({nom}) l'emporte" in issue:
            return cle, emoji, nom
    if "l'emporte seul" in issue:
        return "loupblanc", "🌕", "Loup Blanc"
    return "autre", "🏁", "Fin"
