"""Sauvegarde disque de la partie en cours et archives des parties terminées."""

import glob
import json
import os
from datetime import datetime

from loup_garou.config import HISTORIQUE_DIR, SAVE_FILE


def save_game(s):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def clear_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def archiver_partie(s, issue):
    """Écrit le journal complet dans historique/ (une seule fois par partie terminée)."""
    if s.get("archive"):
        return
    os.makedirs(HISTORIQUE_DIR, exist_ok=True)
    maintenant = datetime.now()
    fichier = os.path.join(HISTORIQUE_DIR, f"partie_{maintenant:%Y%m%d_%H%M%S}.json")
    donnees = {
        "date": maintenant.isoformat(timespec="seconds"),
        "issue": issue,
        "joueurs": s["joueurs"],
        "journal": s["journal"],
    }
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=2, ensure_ascii=False)
    s["archive"] = fichier


def lister_historique():
    """Parties archivées, de la plus récente à la plus ancienne (les fichiers illisibles sont ignorés)."""
    parties = []
    for fichier in sorted(glob.glob(os.path.join(HISTORIQUE_DIR, "partie_*.json")), reverse=True):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                p = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(p, dict) and {"issue", "joueurs", "journal"} <= p.keys():
            parties.append(p)
    return parties


def date_partie(p):
    try:
        return datetime.fromisoformat(p["date"]).strftime("%d/%m/%Y à %H:%M")
    except (KeyError, ValueError):
        return "date inconnue"


def gagnant_partie(issue):
    """(clé CSS, emoji, mot-clé) du camp vainqueur d'après le message de fin."""
    if issue.startswith("Le village a gagné"):
        return "village", "🏡", "Village"
    if issue.startswith("Les loups ont gagné"):
        return "loups", "🐺", "Loups"
    if issue.startswith("Les amoureux"):
        return "couple", "💘", "Couple"
    if "l'emporte seul" in issue:
        return "loupblanc", "🌕", "Loup Blanc"
    return "autre", "🏁", "Fin"
